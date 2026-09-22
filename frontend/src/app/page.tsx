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
import { Bookmark, ChatMessage, Conversation, User } from "@/lib/types";

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

interface ChatAppProps {
  scope: string | null;
  user: User | null;
  onSignOut: () => void;
}

function ChatApp({ scope, user, onSignOut }: ChatAppProps) {
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
  const scopeRef = useRef<string | null>(scope);
  const epochRef = useRef(0);
  const isMountedRef = useRef(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { settings } = useSettings();
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [hasHydrated, setHasHydrated] = useState(false);

  // ---- Load conversations/bookmarks scoped to the signed-in user (or the
  // shared "guest" namespace when signed out). Re-runs whenever the scope
  // changes — because HomePage keys ChatApp by scopeKey, changing accounts
  // or logging in/out mounts a fresh ChatApp instance with clean state. ----
  useEffect(() => {
    isMountedRef.current = true;
    scopeRef.current = scope;
    epochRef.current++;

    const loadedConversations = loadConversations(scope);
    const loadedBookmarks = loadBookmarks(scope);
    setConversations(loadedConversations);
    setBookmarks(loadedBookmarks);

    // Default to a fresh empty chat on initial load or browser refresh,
    // while keeping past conversations accessible in the sidebar history.
    setActiveConversationId(null);

    setHasHydrated(true);

    return () => {
      isMountedRef.current = false;
      pendingRef.current = null;
    };
  }, [scope]);

  // ---- Persist on change, strictly scoped to this component's scope.
  // Guarded against running before hydration or after unmount. ----
  useEffect(() => {
    if (!hasHydrated || !isMountedRef.current) return;
    if (!settings.autoSaveConversations) return;
    saveConversations(conversations, scope);
  }, [conversations, hasHydrated, scope, settings.autoSaveConversations]);

  useEffect(() => {
    if (!hasHydrated || !isMountedRef.current) return;
    saveBookmarks(bookmarks, scope);
  }, [bookmarks, hasHydrated, scope]);

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
    if (!isMountedRef.current) return;
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
    const startScope = scope;
    const startEpoch = epochRef.current;
    updateMessage(conversationId, messageId, { isGraphLoading: true, graphError: null });
    try {
      const graphResult = await getGraph(topic);
      if (
        !isMountedRef.current ||
        scopeRef.current !== startScope ||
        epochRef.current !== startEpoch
      ) {
        return;
      }
      updateMessage(conversationId, messageId, { graph: graphResult, isGraphLoading: false });
    } catch (err) {
      if (
        !isMountedRef.current ||
        scopeRef.current !== startScope ||
        epochRef.current !== startEpoch
      ) {
        return;
      }
      updateMessage(conversationId, messageId, {
        isGraphLoading: false,
        graphError: describeError(err),
      });
    }
  }

  async function runAskStage(
    conversationId: string,
    messageId: string,
    query: string,
    contextTopic?: string | null
  ) {
    const startScope = scope;
    const startEpoch = epochRef.current;

    pendingRef.current = conversationId;
    setPendingConversationId(conversationId);

    function clearPending() {
      if (pendingRef.current === conversationId) pendingRef.current = null;
      if (isMountedRef.current) {
        setPendingConversationId((prev) => (prev === conversationId ? null : prev));
      }
    }

    try {
      const augmentedQuery = buildAugmentedQuery(query, settings);
      const askResult = await askQuestion(augmentedQuery, contextTopic);

      if (
        !isMountedRef.current ||
        scopeRef.current !== startScope ||
        epochRef.current !== startEpoch
      ) {
        return;
      }

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

      if (graphFromAsk === null) {
        await runGraphStage(conversationId, messageId, askResult.topic);
      }
    } catch (err) {
      if (
        !isMountedRef.current ||
        scopeRef.current !== startScope ||
        epochRef.current !== startEpoch
      ) {
        return;
      }
      updateMessage(conversationId, messageId, { askError: describeError(err) });
      clearPending();
    }
  }

  function isContextualFollowUp(query: string): boolean {
    return (
      query.includes("—") ||
      /\b(it|this|that|its|itself|more\s+simply|in\s+detail|revision\s+notes|viva|quiz|prerequisites|how\s+does\s+it\s+work|give\s+an\s+example|working\s+principle)\b/i.test(
        query
      )
    );
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

    const activeTopic = activeConversation
      ? [...activeConversation.messages].reverse().find((m) => m.response?.topic)?.response?.topic ?? null
      : null;
    const contextTopicToPass = isContextualFollowUp(trimmedQuery) ? activeTopic : null;

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

    await runAskStage(conversationId, messageId, trimmedQuery, contextTopicToPass);
  }

  async function handleRetryAsk(messageId: string, query: string) {
    if (!activeConversationId || !activeConversation) return;
    if (pendingRef.current !== null) return;
    updateMessage(activeConversationId, messageId, { askError: null });
    const msgIndex = activeConversation.messages.findIndex((m) => m.id === messageId);
    const priorMessages = msgIndex > 0 ? activeConversation.messages.slice(0, msgIndex) : [];
    const priorTopic =
      [...priorMessages].reverse().find((m) => m.response?.topic)?.response?.topic ?? null;
    const contextTopicToPass = isContextualFollowUp(query) ? priorTopic : null;
    await runAskStage(activeConversationId, messageId, query, contextTopicToPass);
  }

  async function handleRegenerate(messageId: string, query: string) {
    if (!activeConversationId || !activeConversation) return;
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
    const msgIndex = activeConversation.messages.findIndex((m) => m.id === messageId);
    const priorMessages = msgIndex > 0 ? activeConversation.messages.slice(0, msgIndex) : [];
    const priorTopic =
      [...priorMessages].reverse().find((m) => m.response?.topic)?.response?.topic ?? null;
    const contextTopicToPass = isContextualFollowUp(query) ? priorTopic : null;
    await runAskStage(activeConversationId, messageId, query, contextTopicToPass);
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

  function handleClearAllConversations() {
    setConversations([]);
    setActiveConversationId(null);
    saveConversations([], scope);
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
    isMountedRef.current = false;
    scopeRef.current = null;
    pendingRef.current = null;
    epochRef.current++;
    setConversations([]);
    setBookmarks([]);
    setActiveConversationId(null);
    setActiveView("chat");
    onSignOut();
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
        onClearAllConversations={handleClearAllConversations}
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
          onNewChat={handleNewChat}
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

export default function HomePage() {
  const { user, logout, loading: authLoading } = useAuth();

  if (authLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-base text-ink-tertiary">
        <div className="flex items-center gap-2 text-sm">
          <svg
            className="h-4 w-4 animate-spin text-teal"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8H4z"
            />
          </svg>
          Loading...
        </div>
      </div>
    );
  }

  const currentScope = user && user.id != null ? String(user.id) : null;
  const scopeKey = user ? `user_${user.id}_${user.email}` : "guest";

  return (
    <ChatApp
      key={scopeKey}
      scope={currentScope}
      user={user}
      onSignOut={logout}
    />
  );
}
