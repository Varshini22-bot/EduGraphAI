"use client";

import { useMemo, useState } from "react";
import { Conversation } from "@/lib/types";

interface HistoryListProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onRenameConversation: (id: string, title: string) => void;
  onDeleteConversation: (id: string) => void;
  onPinConversation: (id: string) => void;
  onArchiveConversation: (id: string) => void;
}

function formatRelativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// Matches a search term against title, each question, resolved topic, and
// answer text — per "search conversation titles, questions, topics, answers".
function matchesSearch(conversation: Conversation, term: string): boolean {
  const needle = term.toLowerCase();
  if (conversation.title.toLowerCase().includes(needle)) return true;
  return conversation.messages.some((message) => {
    if (message.query.toLowerCase().includes(needle)) return true;
    if (!message.response) return false;
    return (
      message.response.topic.toLowerCase().includes(needle) ||
      message.response.answer.toLowerCase().includes(needle)
    );
  });
}

export default function HistoryList({
  conversations,
  activeConversationId,
  onSelectConversation,
  onRenameConversation,
  onDeleteConversation,
  onPinConversation,
  onArchiveConversation,
}: HistoryListProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draftTitle, setDraftTitle] = useState("");
  const [search, setSearch] = useState("");
  const [showArchived, setShowArchived] = useState(false);

  const filtered = useMemo(() => {
    const term = search.trim();
    return conversations.filter((c) => (term ? matchesSearch(c, term) : true));
  }, [conversations, search]);

  const active = filtered.filter((c) => !c.archived);
  const archived = filtered.filter((c) => c.archived);

  const sorted = [...active].sort((a, b) => {
    if (!!a.pinned !== !!b.pinned) return a.pinned ? -1 : 1;
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });

  function startEditing(conversation: Conversation) {
    setEditingId(conversation.id);
    setDraftTitle(conversation.title);
  }

  function commitEdit() {
    if (editingId && draftTitle.trim()) {
      onRenameConversation(editingId, draftTitle.trim());
    }
    setEditingId(null);
  }

  function renderRow(conversation: Conversation) {
    const isActive = conversation.id === activeConversationId;
    const isEditing = editingId === conversation.id;

    return (
      <div
        key={conversation.id}
        className={`group flex items-center gap-1 rounded-md px-1 transition-colors ${
          isActive ? "border-l-2 border-teal bg-elevated" : "hover:bg-hoverbg"
        }`}
      >
        {isEditing ? (
          <input
            autoFocus
            value={draftTitle}
            onChange={(e) => setDraftTitle(e.target.value)}
            onBlur={commitEdit}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitEdit();
              if (e.key === "Escape") setEditingId(null);
            }}
            className="flex-1 rounded-sm bg-inputbg px-2 py-2 text-[13px] text-ink-primary outline-none"
          />
        ) : (
          <button
            onClick={() => onSelectConversation(conversation.id)}
            className={`flex-1 truncate px-2 py-2 text-left text-[13px] font-medium ${
              isActive ? "text-ink-primary" : "text-ink-secondary group-hover:text-ink-primary"
            }`}
          >
            <span className="flex items-center gap-1 truncate">
              {conversation.pinned && (
                <span className="text-teal" aria-hidden="true">
                  📌
                </span>
              )}
              <span className="truncate">{conversation.title}</span>
            </span>
            <span className="block font-mono text-[11px] text-ink-tertiary">
              {formatRelativeTime(conversation.updatedAt)} · {conversation.messages.length} msg
            </span>
          </button>
        )}

        {!isEditing && (
          <div className="hidden flex-shrink-0 gap-0.5 group-hover:flex">
            <button
              onClick={() => onPinConversation(conversation.id)}
              aria-label={conversation.pinned ? "Unpin conversation" : "Pin conversation"}
              title={conversation.pinned ? "Unpin" : "Pin"}
              className={`flex h-6 w-6 items-center justify-center rounded hover:bg-hoverbg ${
                conversation.pinned ? "text-teal" : "text-ink-tertiary hover:text-ink-primary"
              }`}
            >
              📌
            </button>
            <button
              onClick={() => onArchiveConversation(conversation.id)}
              aria-label={conversation.archived ? "Unarchive conversation" : "Archive conversation"}
              title={conversation.archived ? "Unarchive" : "Archive"}
              className="flex h-6 w-6 items-center justify-center rounded text-ink-tertiary hover:bg-hoverbg hover:text-ink-primary"
            >
              🗄
            </button>
            <button
              onClick={() => startEditing(conversation)}
              aria-label="Rename conversation"
              title="Rename"
              className="flex h-6 w-6 items-center justify-center rounded text-ink-tertiary hover:bg-hoverbg hover:text-ink-primary"
            >
              ✎
            </button>
            <button
              onClick={() => onDeleteConversation(conversation.id)}
              aria-label="Delete conversation"
              title="Delete"
              className="flex h-6 w-6 items-center justify-center rounded text-ink-tertiary hover:bg-danger-dim hover:text-danger"
            >
              ✕
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 pb-3">
      {conversations.length > 0 && (
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search conversations..."
          className="mx-1 rounded-md border border-border-subtle bg-inputbg px-2.5 py-1.5 text-[12.5px] text-ink-primary outline-none placeholder:text-ink-tertiary focus:border-teal"
        />
      )}

      {conversations.length === 0 ? (
        <div className="px-2.5 py-4 text-[12.5px] leading-relaxed text-ink-tertiary">
          No conversations yet. Start a new chat to see it appear here.
        </div>
      ) : sorted.length === 0 ? (
        <div className="px-2.5 py-4 text-[12.5px] leading-relaxed text-ink-tertiary">
          No conversations match &quot;{search}&quot;.
        </div>
      ) : (
        <div className="flex flex-col gap-0.5">{sorted.map(renderRow)}</div>
      )}

      {archived.length > 0 && (
        <div className="px-1">
          <button
            onClick={() => setShowArchived((v) => !v)}
            className="text-[11.5px] text-ink-tertiary hover:text-ink-primary"
          >
            {showArchived ? "Hide" : "Show"} archived ({archived.length})
          </button>
          {showArchived && (
            <div className="mt-1 flex flex-col gap-0.5">{archived.map(renderRow)}</div>
          )}
        </div>
      )}
    </div>
  );
}
