"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useSettings } from "@/context/SettingsContext";
import { useToast } from "@/context/ToastContext";
import ConfirmDialog from "@/components/ConfirmDialog";
import Toggle from "@/components/Toggle";
import {
  loadConversations,
  saveConversations,
  loadBookmarks,
  saveBookmarks,
} from "@/lib/storage";
import {
  AnswerStyle,
  LearningLevel,
  ThemePreference,
} from "@/lib/settingsStorage";

type CategoryId =
  | "account"
  | "appearance"
  | "learning"
  | "chat"
  | "graph"
  | "data";

const CATEGORIES: { id: CategoryId; label: string; icon: string }[] = [
  { id: "account", label: "Account", icon: "◔" },
  { id: "appearance", label: "Appearance", icon: "◐" },
  { id: "learning", label: "Learning", icon: "✦" },
  { id: "chat", label: "Chat", icon: "◈" },
  { id: "graph", label: "Knowledge Graph", icon: "◎" },
  { id: "data", label: "Data & Privacy", icon: "◧" },
];

function SegmentedControl<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={`rounded-full border px-3.5 py-1.5 text-[12.5px] font-medium transition-colors ${
            value === option.value
              ? "border-teal bg-teal-dim text-teal"
              : "border-border-subtle bg-elevated text-ink-secondary hover:border-border-strong hover:text-ink-primary"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

function formatMemberSince(value: unknown): string {
  if (typeof value !== "string") return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function SettingsPage() {
  const { user, loading, logout } = useAuth();
  const { settings, updateSetting, resolvedTheme } = useSettings();
  const { showToast } = useToast();
  const router = useRouter();

  const [activeCategory, setActiveCategory] = useState<CategoryId>("account");
  const [confirmAction, setConfirmAction] = useState<
    "clear-conversations" | "clear-bookmarks" | null
  >(null);

  function handleExportConversations() {
    const data = loadConversations();
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `knowledge-graph-conversations-${new Date()
      .toISOString()
      .slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    showToast("Conversations exported.");
  }

  function handleConfirmDestructive() {
    if (confirmAction === "clear-conversations") {
      saveConversations([]);
      showToast("All conversations cleared.");
    } else if (confirmAction === "clear-bookmarks") {
      saveBookmarks([]);
      showToast("All bookmarks cleared.");
    }
    setConfirmAction(null);
  }

  function handleLogout() {
    logout();
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-base p-8">
        <p className="mx-auto max-w-3xl text-ink-secondary">Loading settings...</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-3 bg-base px-4 text-center">
        <p className="text-[14px] text-ink-secondary">
          You need to be signed in to view settings.
        </p>
        <Link href="/login" className="btn-primary">
          Sign In
        </Link>
      </main>
    );
  }

  const displayName = user.full_name || user.email;
  const memberSince = formatMemberSince(user.created_at);

  return (
    <main className="min-h-screen bg-base px-4 py-8 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/"
          className="mb-6 inline-block text-[13px] text-ink-tertiary hover:text-ink-primary"
        >
          ← Back to app
        </Link>

        <div className="mb-7">
          <h1 className="font-display text-2xl font-bold text-ink-primary">Settings</h1>
          <p className="mt-1 text-sm text-ink-secondary">
            Manage your account and assistant preferences.
          </p>
        </div>

        {/* Mobile: horizontal scrollable tabs. Desktop: left nav (below). */}
        <div className="mb-5 flex gap-2 overflow-x-auto pb-1 md:hidden">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex flex-shrink-0 items-center gap-1.5 rounded-full border px-3.5 py-2 text-[12.5px] font-medium transition-colors ${
                activeCategory === cat.id
                  ? "border-teal bg-teal-dim text-teal"
                  : "border-border-subtle bg-elevated text-ink-secondary"
              }`}
            >
              <span aria-hidden="true">{cat.icon}</span>
              {cat.label}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr]">
          {/* Desktop left nav */}
          <nav className="hidden md:block">
            <div className="card sticky top-6 flex flex-col gap-0.5 p-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-[13px] font-medium transition-colors ${
                    activeCategory === cat.id
                      ? "bg-teal-dim text-teal"
                      : "text-ink-secondary hover:bg-hoverbg hover:text-ink-primary"
                  }`}
                >
                  <span aria-hidden="true">{cat.icon}</span>
                  {cat.label}
                </button>
              ))}
            </div>
          </nav>

          {/* Content */}
          <div className="min-w-0">
            {activeCategory === "account" && (
              <section className="card px-6 py-6">
                <h2 className="mb-5 text-[15px] font-semibold text-ink-primary">Account</h2>
                <div className="flex items-center gap-4 border-b border-border-subtle pb-5">
                  <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet to-violet text-lg font-bold text-white">
                    {displayName.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <div className="truncate text-[15px] font-semibold text-ink-primary">
                      {displayName}
                    </div>
                    <div className="truncate text-[13px] text-ink-tertiary">{user.email}</div>
                  </div>
                </div>
                <div className="flex items-center justify-between border-b border-border-subtle py-3.5">
                  <span className="text-[13px] text-ink-secondary">Account status</span>
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                      user.is_active ? "bg-teal-dim text-teal" : "bg-danger-dim text-danger"
                    }`}
                  >
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="flex items-center justify-between py-3.5">
                  <span className="text-[13px] text-ink-secondary">Member since</span>
                  <span className="text-[13px] font-medium text-ink-primary">{memberSince}</span>
                </div>
              </section>
            )}

            {activeCategory === "appearance" && (
              <section className="card px-6 py-6">
                <h2 className="mb-1 text-[15px] font-semibold text-ink-primary">Appearance</h2>
                <p className="mb-5 text-[12.5px] text-ink-secondary">
                  Currently resolved to <strong className="text-ink-primary">{resolvedTheme}</strong> mode.
                </p>
                <div className="border-b border-border-subtle pb-5">
                  <div className="mb-2 text-[13.5px] font-medium text-ink-primary">Theme</div>
                  <SegmentedControl<ThemePreference>
                    value={settings.theme}
                    onChange={(v) => updateSetting("theme", v)}
                    options={[
                      { value: "system", label: "System" },
                      { value: "light", label: "Light" },
                      { value: "dark", label: "Dark" },
                    ]}
                  />
                </div>
                <div className="pt-3.5">
                  <Toggle
                    label="Compact mode"
                    description="Reduces spacing in chat messages and cards."
                    checked={settings.compactMode}
                    onChange={(v) => updateSetting("compactMode", v)}
                  />
                </div>
              </section>
            )}

            {activeCategory === "learning" && (
              <section className="card px-6 py-6">
                <h2 className="mb-5 text-[15px] font-semibold text-ink-primary">
                  Learning Preferences
                </h2>
                <div className="border-b border-border-subtle pb-5">
                  <div className="mb-2 text-[13.5px] font-medium text-ink-primary">
                    Answer style
                  </div>
                  <SegmentedControl<AnswerStyle>
                    value={settings.answerStyle}
                    onChange={(v) => updateSetting("answerStyle", v)}
                    options={[
                      { value: "simple", label: "Simple" },
                      { value: "detailed", label: "Detailed" },
                      { value: "exam-friendly", label: "Exam-friendly" },
                    ]}
                  />
                  <p className="mt-2 text-[11.5px] text-ink-tertiary">
                    Applied to how each answer is displayed. The backend doesn't
                    yet accept this as a generation parameter, so this changes
                    presentation, not what the AI generates.
                  </p>
                </div>
                <div className="border-b border-border-subtle py-5">
                  <div className="mb-2 text-[13.5px] font-medium text-ink-primary">
                    Learning level
                  </div>
                  <SegmentedControl<LearningLevel>
                    value={settings.learningLevel}
                    onChange={(v) => updateSetting("learningLevel", v)}
                    options={[
                      { value: "beginner", label: "Beginner" },
                      { value: "intermediate", label: "Intermediate" },
                      { value: "advanced", label: "Advanced" },
                    ]}
                  />
                  <p className="mt-2 text-[11.5px] text-ink-tertiary">
                    Shown as a badge on each answer. The backend doesn't yet
                    tailor content by level, so wording itself doesn't change.
                  </p>
                </div>
                <div className="pt-3.5">
                  <Toggle
                    label="Show graph context"
                    description="Controls the Knowledge Graph visualization in each answer."
                    checked={settings.showGraphContext}
                    onChange={(v) => updateSetting("showGraphContext", v)}
                  />
                  <Toggle
                    label="Show learning path"
                    checked={settings.showLearningPath}
                    onChange={(v) => updateSetting("showLearningPath", v)}
                  />
                  <Toggle
                    label="Show recommendations"
                    checked={settings.showRecommendations}
                    onChange={(v) => updateSetting("showRecommendations", v)}
                  />
                </div>
              </section>
            )}

            {activeCategory === "chat" && (
              <section className="card px-6 py-6">
                <h2 className="mb-2 text-[15px] font-semibold text-ink-primary">
                  Chat Preferences
                </h2>
                <div className="divide-y divide-border-subtle">
                  <Toggle
                    label="Enter to send"
                    description={
                      settings.enterToSend
                        ? "Enter sends your message; Shift+Enter adds a new line."
                        : "Enter adds a new line; use the send button or Ctrl+Enter to send."
                    }
                    checked={settings.enterToSend}
                    onChange={(v) => updateSetting("enterToSend", v)}
                  />
                  <Toggle
                    label="Auto-save conversations"
                    description="When off, conversations won't persist across a page refresh."
                    checked={settings.autoSaveConversations}
                    onChange={(v) => updateSetting("autoSaveConversations", v)}
                  />
                </div>
              </section>
            )}

            {activeCategory === "graph" && (
              <section className="card px-6 py-6">
                <h2 className="mb-1 text-[15px] font-semibold text-ink-primary">
                  Knowledge Graph Preferences
                </h2>
                <p className="mb-4 text-[12.5px] text-ink-secondary">
                  Controls what appears inside the graph visualization (requires
                  &quot;Show graph context&quot; in Learning to be on).
                </p>
                <div className="divide-y divide-border-subtle">
                  <Toggle
                    label="Show related topics"
                    checked={settings.showRelatedTopics}
                    onChange={(v) => updateSetting("showRelatedTopics", v)}
                  />
                  <Toggle
                    label="Show incoming relationships"
                    checked={settings.showIncomingRelationships}
                    onChange={(v) => updateSetting("showIncomingRelationships", v)}
                  />
                  <Toggle
                    label="Show outgoing relationships"
                    checked={settings.showOutgoingRelationships}
                    onChange={(v) => updateSetting("showOutgoingRelationships", v)}
                  />
                </div>
              </section>
            )}

            {activeCategory === "data" && (
              <>
                <section className="card mb-6 px-6 py-6">
                  <h2 className="mb-2 text-[15px] font-semibold text-ink-primary">
                    Data &amp; Privacy
                  </h2>
                  <div className="divide-y divide-border-subtle">
                    <div className="flex items-center justify-between py-3.5">
                      <div className="text-[13.5px] font-medium text-ink-primary">
                        Export conversations
                      </div>
                      <button
                        onClick={handleExportConversations}
                        className="btn-ghost !px-3 !py-1.5 text-xs"
                      >
                        Export
                      </button>
                    </div>
                    <div className="flex items-center justify-between py-3.5">
                      <div className="text-[13.5px] font-medium text-ink-primary">
                        Clear all conversations
                      </div>
                      <button
                        onClick={() => setConfirmAction("clear-conversations")}
                        className="rounded-md border border-danger px-3 py-1.5 text-xs font-semibold text-danger transition-colors hover:bg-danger-dim"
                      >
                        Clear
                      </button>
                    </div>
                    <div className="flex items-center justify-between py-3.5">
                      <div className="text-[13.5px] font-medium text-ink-primary">
                        Clear bookmarks
                      </div>
                      <button
                        onClick={() => setConfirmAction("clear-bookmarks")}
                        className="rounded-md border border-danger px-3 py-1.5 text-xs font-semibold text-danger transition-colors hover:bg-danger-dim"
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                </section>

                <section className="card px-6 py-6">
                  <h2 className="mb-2 text-[15px] font-semibold text-ink-primary">
                    Account Actions
                  </h2>
                  <div className="divide-y divide-border-subtle">
                    <div className="flex items-center justify-between py-3.5">
                      <div className="text-[13.5px] font-medium text-ink-primary">Logout</div>
                      <button onClick={handleLogout} className="btn-ghost !px-3 !py-1.5 text-xs">
                        Logout
                      </button>
                    </div>
                    <div className="flex items-center justify-between py-3.5">
                      <div>
                        <div className="text-[13.5px] font-medium text-ink-primary">
                          Delete account
                        </div>
                        <div className="mt-0.5 max-w-sm text-[12px] text-ink-tertiary">
                          Not currently available — no delete-account endpoint
                          exists on the backend.
                        </div>
                      </div>
                      <button
                        disabled
                        className="cursor-not-allowed rounded-md border border-border-subtle px-3 py-1.5 text-xs font-semibold text-ink-tertiary opacity-60"
                      >
                        Not available
                      </button>
                    </div>
                  </div>
                </section>
              </>
            )}
          </div>
        </div>
      </div>

      <ConfirmDialog
        isOpen={confirmAction !== null}
        title={
          confirmAction === "clear-conversations"
            ? "Delete all conversations?"
            : "Delete all bookmarks?"
        }
        description="This action cannot be undone."
        onConfirm={handleConfirmDestructive}
        onCancel={() => setConfirmAction(null)}
      />
    </main>
  );
}
