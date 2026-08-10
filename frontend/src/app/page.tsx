"use client";

import { useEffect, useState } from "react";
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
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const { settings } = useSettings();
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [hasHydrated, setHasHydrated] = useState(false);

  // ---- Load conversations/bookmarks from localStorage once, on mount ----
  // (user/session loading is handled entirely by AuthProvider, not here)
  useEffect(() => {
    const loadedConversations = loadConversations();
    const loadedBookmarks = loadBookmarks();
    setConversations(loadedConversations);
    setBookmarks(loadedBookmarks);

    if (loadedConversations.length > 0) {
      const mostRecent = [...loadedConversations].sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      )[0];
      setActiveConversationId(mostRecent.id);
    }

    setHasHydrated(true);
  }, []);

  // ---- Persist on every change (guarded so we don't clobber storage
  // with the empty initial state before hydration finishes) ----
  useEffect(() => {
    if (!hasHydrated) return;
    // "Auto-save conversations" gates persistence to localStorage only —
    // in-session state (switching conversations, asking questions) keeps
    // working identically either way; disabling it just means nothing
    // survives a refresh.
    if (!settings.autoSaveConversations) return;
    saveConversations(conversations);
  }, [conversations, hasHydrated, settings.autoSaveConversations]);

  useEffect(() => {
    if (!hasHydrated) return;
    saveBookmarks(bookmarks);
  }, [bookmarks, hasHydrated]);

  const activeConversation =
    conversations.find((c) => c.id === activeConversationId) ?? null;

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
    updateMessage(conversationId, messageId, { isGraphLoading: true, graphError: null });
    try {
      const graphResult = await getGraph(topic);
      updateMessage(conversationId, messageId, { graph: graphResult, isGraphLoading: false });
    } catch (err) {
      updateMessage(conversationId, messageId, {
        isGraphLoading: false,
        graphError: describeError(err),
      });
    }
  }

  async function runAskStage(conversationId: string, messageId: string, query: string) {
    try {
      // Encodes marks/explanation-mode intent into the actual request text
      // (real effect on what the LLM sees) — the displayed user message
      // stays exactly what they typed; only the backend-bound copy changes.
      const augmentedQuery = buildAugmentedQuery(query, settings);
      const askResult = await askQuestion(augmentedQuery);

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
                ? { ...message, response: askResult, askError: null }
                : message
            ),
          };
        })
      );

      setIsLoading(false);
      // Graph loads after the answer is displayed, keyed by the resolved
      // topic (askResult.topic) — the backend's /graph/topic/{topic_name}
      // route matches on an exact topic name, not the user's free-text query.
      await runGraphStage(conversationId, messageId, askResult.topic);
    } catch (err) {
      updateMessage(conversationId, messageId, { askError: describeError(err) });
      setIsLoading(false);
    }
  }

  async function handleSubmitQuery(query: string) {
    setActiveView("chat");
    setIsLoading(true);

    let conversationId = activeConversationId;
    const messageId = createId("msg");
    const timestamp = nowIso();

    const newMessage: ChatMessage = {
      id: messageId,
      query,
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
        title: query,
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

    await runAskStage(conversationId, messageId, query);
  }

  async function handleRetryAsk(messageId: string, query: string) {
    if (!activeConversationId) return;
    updateMessage(activeConversationId, messageId, { askError: null });
    setIsLoading(true);
    await runAskStage(activeConversationId, messageId, query);
  }

  async function handleRegenerate(messageId: string, query: string) {
    if (!activeConversationId) return;
    updateMessage(activeConversationId, messageId, {
      response: null,
      graph: null,
      isGraphLoading: false,
      askError: null,
      graphError: null,
    });
    setIsLoading(true);
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
        onNewChat={handleNewChat}
        user={user}
        onSignOut={logout}
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
