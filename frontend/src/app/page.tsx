"use client";

import { useEffect, useRef, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import ConversationContainer from "@/components/chat/ConversationContainer";
import ProgressDashboard from "@/components/ProgressDashboard";
import BookmarkList from "@/components/BookmarkList";
import { ApiError, askQuestion, getGraph } from "@/lib/api";
import {
  loadBookmarks,
  loadConversations,
  saveBookmarks,
  saveConversations,
} from "@/lib/storage";
import { computeDashboardMetrics } from "@/lib/metrics";
import { buildAugmentedQuery } from "@/lib/answerIntent";
import { useAuth } from "@/context/AuthContext";
import { useSettings } from "@/context/SettingsContext";
import { Bookmark, ChatMessage, Conversation } from "@/lib/types";

type ActiveView = "chat" | "dashboard" | "bookmarks";

function createId(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong. Please try again.";
}

function nowIso(): string {
  return new Date().toISOString();
}

export default function HomePage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<ActiveView>("chat");
  // ---- Which conversation currently has an /ask request in flight (null =
  // none). Tracked PER CONVERSATION rather than as one global boolean: with a
  // global flag, starting an answer in chat A and switching to chat B showed
  // B a "Thinking..." indicator and disabled B's input, even though nothing
  // was pending there. ----
  const [pendingConversationId, setPendingConversationId] = useState<string | null>(null);
  // Synchronous mirror of the above, used for the duplicate-request guard.
  // setState is asynchronous, so two clicks landing in the same tick would
  // both still observe the old state; a ref is updated immediately and is
  // what actually makes the guard reliable.
  const pendingRef = useRef<string | null>(null);
  // The scope (user id, or null for guest) that in-flight async work was
  // started under. Compared after every await so a response belonging to the
  // PREVIOUS user can never be written into the new user's state.
  const scopeRef = useRef<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout, loading: authLoading } = useAuth();
  const { settings } = useSettings();
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [hasHydrated, setHasHydrated] = useState(false);
  // Tracks which scope (signed-in user id, or null for guest) the current
  // `conversations`/`bookmarks` state actually belongs to. This is what
  // lets the save effects below detect "the scope just changed but state
  // hasn't caught up yet" and skip that one stale pass, instead of writing
  // the previous user's data into the new scope's storage key.
  const [activeScope, setActiveScope] = useState<string | null>(null);

  // ---- Load conversations/bookmarks scoped to the signed-in user (or the
  // shared "guest" namespace when signed out). Re-runs whenever the user
  // signs in/out while the app is open, not just once on mount — this is
  // what fixes one user's chats being visible to the next person on the
  // same browser. ----
  useEffect(() => {
    if (authLoading) return;
    const scope = user ? String(user.id) : null;

    // Record the scope all subsequent async work runs under, and release any
    // in-flight request lock: anything still pending was started by the
    // PREVIOUS user, so its loading state must not carry over and its result
    // is discarded by the scopeRef checks in runAskStage/runGraphStage.
    scopeRef.current = scope;
    pendingRef.current = null;
    setPendingConversationId(null);

    const loadedConversations = loadConversations(scope);
    const loadedBookmarks = loadBookmarks(scope);
    setConversations(loadedConversations);
    setBookmarks(loadedBookmarks);
    setActiveScope(scope);

    if (loadedConversations.length > 0) {
      const mostRecent = [...loadedConversations].sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      )[0];
      setActiveConversationId(mostRecent.id);
    } else {
      setActiveConversationId(null);
    }

    setHasHydrated(true);
  }, [authLoading, user?.id]);

  // ---- Persist on every change. Guarded on activeScope matching the
  // CURRENT user — on the render where user?.id has just changed but the
  // load effect above hasn't committed its setState yet, activeScope still
  // reflects the OLD scope, so this correctly skips that one stale pass
  // instead of saving old data under the new scope's key. ----
  useEffect(() => {
    if (!hasHydrated) return;
    if (activeScope !== (user ? String(user.id) : null)) return;
    // "Auto-save conversations" gates persistence to localStorage only —
    // in-session state (switching conversations, asking questions) keeps
    // working identically either way; disabling it just means nothing
    // survives a refresh.
    if (!settings.autoSaveConversations) return;
    saveConversations(conversations, activeScope);
  }, [conversations, hasHydrated, activeScope, user, settings.autoSaveConversations]);

  useEffect(() => {
    if (!hasHydrated) return;
    if (activeScope !== (user ? String(user.id) : null)) return;
    saveBookmarks(bookmarks, activeScope);
  }, [bookmarks, hasHydrated, activeScope, user]);

  const activeConversation =
    conversations.find((c) => c.id === activeConversationId) ?? null;

  // Derived from pendingConversationId (the per-conversation pending marker)
  // rather than a separate boolean, so a request started in one chat can
  // never show "Thinking..." or disable the composer in a different chat.
  const isLoading =
    pendingConversationId !== null && pendingConversationId === activeConversationId;

  // Whether ANY conversation has a request in flight. handleSubmitQuery
  // permits only one /ask at a time app-wide, so the composer has to honour
  // that global limit even though the "Thinking..." indicator above stays
  // per-conversation. Previously the two disagreed: in a chat that wasn't
  // the pending one the composer looked ready, so a question typed there
  // was accepted by the UI, cleared from the textarea on send, and then
  // dropped by the guard with no message and no error shown.
  const isAnyRequestPending = pendingConversationId !== null;

  const lastMessage =
    activeConversation && activeConversation.messages.length > 0
      ? activeConversation.messages[activeConversation.messages.length - 1]
      : null;

  const isCurrentTopicBookmarked =
    lastMessage && lastMessage.response
      ? bookmarks.some((b) => b.topic === lastMessage.response!.topic)
      : false;

  const dashboardMetrics = computeDashboardMetrics(conversations, bookmarks);

  function updateMessage(
    conversationId: string,
    messageId: string,
    patch: Partial<ChatMessage>
  ) {
    setConversations((prev) =>
      prev.map((conversation) => {
        if (conversation.id !== conversationId) return conversation;
        return {
          ...conversation,
          updatedAt: nowIso(),
          messages: conversation.messages.map((message) =>
            message.id === messageId ? { ...message, ...patch } : message
          ),
        };
      })
    );
  }

  async function runGraphStage(conversationId: string, messageId: string, topic: string) {
    // Scope this request belongs to. Compared again after the await so a
    // graph result fetched for the PREVIOUS user (or for guest, before a
    // login) is dropped instead of being written into the new user's state.
    const startScope = scopeRef.current;
    updateMessage(conversationId, messageId, { isGraphLoading: true, graphError: null });
    try {
      const graphResult = await getGraph(topic);
      if (scopeRef.current !== startScope) return;
      updateMessage(conversationId, messageId, { graph: graphResult, isGraphLoading: false });
    } catch (err) {
      if (scopeRef.current !== startScope) return;
      updateMessage(conversationId, messageId, {
        isGraphLoading: false,
        graphError: describeError(err),
      });
    }
  }

  async function runAskStage(conversationId: string, messageId: string, query: string) {
    // Scope this request belongs to (see runGraphStage). Re-checked after the
    // await so an answer for the previous user is discarded, not displayed.
    const startScope = scopeRef.current;

    // Mark this conversation pending: the ref is updated synchronously (so
    // the duplicate-request guard sees it immediately, even for two clicks
    // in the same tick), the state drives the UI.
    pendingRef.current = conversationId;
    setPendingConversationId(conversationId);

    function clearPending() {
      if (pendingRef.current === conversationId) pendingRef.current = null;
      setPendingConversationId((prev) => (prev === conversationId ? null : prev));
    }

    try {
      // Encodes marks/explanation-mode intent into the actual request text
      // (real effect on what the LLM sees) — the displayed user message
      // stays exactly what they typed; only the backend-bound copy changes.
      const augmentedQuery = buildAugmentedQuery(query, settings);
      const askResult = await askQuestion(augmentedQuery);

      // Auth scope changed mid-flight (login/logout/user switch). This answer
      // belongs to the previous scope, so drop it. The hydration effect has
      // already reset the pending markers for the new scope.
      if (scopeRef.current !== startScope) return;

      // The knowledge graph now arrives INSIDE the /ask response (api.ts
      // builds it from the outgoing/incoming relationships the backend
      // already returned), so it is committed in the SAME state update as
      // the answer. Previously this triggered a second, sequential
      // GET /graph/topic request that re-ran the exact Cypher the backend
      // had just run — the user watched a graph spinner after already
      // having waited for the LLM.
      const graphFromAsk = askResult.graph ?? null;

      setConversations((prev) =>
        prev.map((conversation) => {
          if (conversation.id !== conversationId) return conversation;
          const isFirstMessage = conversation.messages[0]?.id === messageId;
          return {
            ...conversation,
            title: isFirstMessage ? askResult.topic : conversation.title,
            updatedAt: nowIso(),
            messages: conversation.messages.map((message) =>
              message.id === messageId
                ? {
                    ...message,
                    response: askResult,
                    askError: null,
                    graph: graphFromAsk,
                    isGraphLoading: false,
                    graphError: null,
                  }
                : message
            ),
          };
        })
      );

      clearPending();

      // Defensive fallback only. askQuestion() always returns a graph on
      // success, so this normally never runs — it exists so that if the
      // response ever lacks one, the graph is still fetched the old way
      // instead of silently disappearing from the UI.
      if (graphFromAsk === null) {
        await runGraphStage(conversationId, messageId, askResult.topic);
      }
    } catch (err) {
      if (scopeRef.current !== startScope) return;
      updateMessage(conversationId, messageId, { askError: describeError(err) });
      clearPending();
    }
  }

  async function handleSubmitQuery(query: string) {
    // ChatInput already blocks blank sends, but topic chips, bookmarks and
    // quick actions call in here too — so the guard lives here as well.
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;

    // One /ask in flight at a time. Checked against the ref (not state)
    // because setState is async: two clicks in the same tick would both see
    // the stale value and each append a message + fire a request.
    if (pendingRef.current !== null) return;

    setActiveView("chat");

    let conversationId = activeConversationId;
    const messageId = createId("msg");
    const timestamp = nowIso();

    const newMessage: ChatMessage = {
      id: messageId,
      query: trimmedQuery,
      timestamp,
      response: null,
      graph: null,
      isGraphLoading: false,
      askError: null,
      graphError: null,
    };

    if (!conversationId || !activeConversation) {
      const newConversation: Conversation = {
        id: createId("conv"),
        title: trimmedQuery,
        createdAt: timestamp,
        updatedAt: timestamp,
        messages: [newMessage],
      };
      conversationId = newConversation.id;
      setConversations((prev) => [newConversation, ...prev]);
      setActiveConversationId(newConversation.id);
    } else {
      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === conversationId
            ? { ...conversation, updatedAt: timestamp, messages: [...conversation.messages, newMessage] }
            : conversation
        )
      );
    }

    await runAskStage(conversationId, messageId, trimmedQuery);
  }

  async function handleRetryAsk(messageId: string, query: string) {
    if (!activeConversationId) return;
    if (pendingRef.current !== null) return;
    updateMessage(activeConversationId, messageId, { askError: null });
    await runAskStage(activeConversationId, messageId, query);
  }

  async function handleRegenerate(messageId: string, query: string) {
    if (!activeConversationId) return;
    if (pendingRef.current !== null) return;
    // Clears the previous answer for THIS message id only, then re-runs the
    // same stage against the same id — so the regenerated answer replaces the
    // correct response instead of appending a new exchange.
    updateMessage(activeConversationId, messageId, {
      response: null,
      graph: null,
      isGraphLoading: false,
      askError: null,
      graphError: null,
    });
    await runAskStage(activeConversationId, messageId, query);
  }

  async function handleRetryGraph(messageId: string, _query: string) {
    if (!activeConversationId || !activeConversation) return;
    // ChatMessage.tsx passes message.query (the original question) here
    // unchanged — we don't touch that component. Instead, resolve the
    // actual resolved topic from state, since /graph/topic/{topic_name}
    // must be called with the topic, not the raw question.
    const message = activeConversation.messages.find((m) => m.id === messageId);
    const topic = message?.response?.topic;
    if (!topic) return;
    await runGraphStage(activeConversationId, messageId, topic);
  }

  function handleNewChat() {
    const timestamp = nowIso();
    const newConversation: Conversation = {
      id: createId("conv"),
      title: "New Chat",
      createdAt: timestamp,
      updatedAt: timestamp,
      messages: [],
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setActiveView("chat");
    setSidebarOpen(false);
  }

  function handleRenameConversation(id: string, title: string) {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, title, updatedAt: nowIso() } : c))
    );
  }

  function handleDeleteConversation(id: string) {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      setActiveConversationId(null);
    }
  }

  function handlePinConversation(id: string) {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, pinned: !c.pinned, updatedAt: nowIso() } : c))
    );
  }

  function handleArchiveConversation(id: string) {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, archived: !c.archived, updatedAt: nowIso() } : c))
    );
  }

  function handleToggleBookmark(topic: string, answer: string) {
    setBookmarks((prev) => {
      const existing = prev.find((b) => b.topic === topic);
      if (existing) return prev.filter((b) => b.id !== existing.id);
      const newBookmark: Bookmark = {
        id: createId("bm"),
        topic,
        answerSnippet: answer.slice(0, 120) + "...",
        savedAt: nowIso(),
      };
      return [newBookmark, ...prev];
    });
  }

  function handleToggleBookmarkForLastMessage() {
    if (!lastMessage || !lastMessage.response) return;
    handleToggleBookmark(lastMessage.response.topic, lastMessage.response.answer);
  }

  function handleRemoveBookmark(id: string) {
    setBookmarks((prev) => prev.filter((b) => b.id !== id));
  }

  function handleOpenBookmark(topic: string) {
    setActiveView("chat");
    handleSubmitQuery(topic);
  }

  function handleChangeView(view: "dashboard" | "bookmarks") {
    setActiveView(view);
    setSidebarOpen(false);
  }

  function handleSignOut() {
    // Storage is scoped per user (storage.ts + the hydration effect above),
    // so signing out never needs to delete anything from localStorage — the
    // guest namespace is already a separate key from this user's.
    //
    // Three things must happen immediately, before the auth state change has
    // re-rendered:
    //  1. scopeRef is advanced so any /ask or /graph response still in flight
    //     for this user fails its post-await scope check and is discarded
    //     instead of landing in guest state.
    //  2. The pending markers are released so this user's "Thinking..."
    //     indicator can't carry over into the guest session.
    //  3. In-memory conversations/bookmarks are emptied so the previous
    //     user's messages are off screen on the very next frame.
    // The save effects are guarded on activeScope === current user, so the
    // cleared arrays are never written into either scope's storage key.
    scopeRef.current = null;
    pendingRef.current = null;
    setPendingConversationId(null);
    setConversations([]);
    setBookmarks([]);
    setActiveConversationId(null);
    setActiveView("chat");
    logout();
  }

  function navbarTitle(): string {
    if (activeView === "dashboard") return "Progress Dashboard";
    if (activeView === "bookmarks") return "Bookmarks";
    return activeConversation?.title ?? "New Chat";
  }

  function navbarSubtitle(): string | undefined {
    if (activeView !== "chat") return undefined;
    return activeConversation && activeConversation.messages.length > 0
      ? `${activeConversation.messages.length} exchange${
          activeConversation.messages.length > 1 ? "s" : ""
        }`
      : "Start a new conversation";
  }

  return (
    <div className="flex">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => {
          setActiveConversationId(id);
          setActiveView("chat");
          setSidebarOpen(false);
        }}
        onRenameConversation={handleRenameConversation}
        onDeleteConversation={handleDeleteConversation}
        onPinConversation={handlePinConversation}
        onArchiveConversation={handleArchiveConversation}
        onNewChat={handleNewChat}
        user={user}
        onSignOut={handleSignOut}
        activeView={activeView}
        onChangeView={handleChangeView}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="min-w-0 flex-1 md:ml-0">
        <Navbar
          title={navbarTitle()}
          subtitle={navbarSubtitle()}
          onOpenSidebar={() => setSidebarOpen(true)}
          showBookmarkAction={activeView === "chat" && !!lastMessage?.response}
          isBookmarked={isCurrentTopicBookmarked}
          onToggleBookmark={handleToggleBookmarkForLastMessage}
        />

        {activeView === "chat" && (
          <ConversationContainer
            conversation={activeConversation}
            isLoading={isLoading}
            isSendBlocked={isAnyRequestPending}
            onSubmitQuery={handleSubmitQuery}
            onRetryAsk={handleRetryAsk}
            onRetryGraph={handleRetryGraph}
            onRegenerate={handleRegenerate}
            bookmarkedTopics={bookmarks.map((b) => b.topic)}
            onToggleBookmark={handleToggleBookmark}
          />
        )}

        {activeView === "dashboard" && (
          <ProgressDashboard metrics={dashboardMetrics} />
        )}

        {activeView === "bookmarks" && (
          <BookmarkList
            bookmarks={bookmarks}
            onOpen={handleOpenBookmark}
            onRemove={handleRemoveBookmark}
          />
        )}
      </main>
    </div>
  );
}
