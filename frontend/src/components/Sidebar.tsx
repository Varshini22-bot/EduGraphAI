"use client";

import { useState } from "react";
import Link from "next/link";
import { Conversation, User } from "@/lib/types";
import HistoryList from "./HistoryList";
import AccountMenu from "./account/AccountMenu";
import UsageIndicator from "./UsageIndicator";
import PricingModal from "./PricingModal";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  usageRefreshKey?: number;
  onSelectConversation: (id: string) => void;
  onRenameConversation: (id: string, title: string) => void;
  onDeleteConversation: (id: string) => void;
  onPinConversation: (id: string) => void;
  onArchiveConversation: (id: string) => void;
  onNewChat: () => void;
  user: User | null;
  onSignOut: () => void;
  activeView: "chat" | "dashboard" | "bookmarks";
  onChangeView: (view: "dashboard" | "bookmarks") => void;
  isOpen: boolean;
  onClose: () => void;
}

function BrandMark() {
  return (
    <svg width="30" height="30" viewBox="0 0 30 30" fill="none" aria-hidden="true" className="flex-shrink-0">
      <line x1="7" y1="8" x2="15" y2="22" stroke="#45d6c6" strokeWidth="1.4" />
      <line x1="23" y1="8" x2="15" y2="22" stroke="#45d6c6" strokeWidth="1.4" />
      <line x1="7" y1="8" x2="23" y2="8" stroke="#343b4d" strokeWidth="1.4" />
      <circle cx="7" cy="8" r="3.4" fill="#1b1f2a" stroke="#8b7ff0" strokeWidth="1.6" />
      <circle cx="23" cy="8" r="3.4" fill="#1b1f2a" stroke="#8b7ff0" strokeWidth="1.6" />
      <circle cx="15" cy="22" r="4" fill="#45d6c6" />
    </svg>
  );
}

export default function Sidebar({
  conversations,
  activeConversationId,
  usageRefreshKey,
  onSelectConversation,
  onRenameConversation,
  onDeleteConversation,
  onNewChat,
  user,
  onSignOut,
  activeView,
  onChangeView,
  isOpen,
  onClose,
}: SidebarProps) {
  // Desktop-only collapse to an icon rail. Self-contained here since no
  // other component needs to know about it (mobile keeps the existing
  // drawer behavior via isOpen/onClose, untouched).
  const [collapsed, setCollapsed] = useState(false);
  const [pricingOpen, setPricingOpen] = useState(false);

  return (
    <>
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-[55] bg-black/50 md:hidden"
        />
      )}
      <aside
        aria-label="Sidebar navigation"
        className={`fixed left-0 top-0 z-[60] flex h-screen w-[272px] flex-shrink-0 flex-col border-r border-border-subtle bg-surface transition-[transform,width] duration-200 md:sticky md:translate-x-0 ${
          isOpen ? "translate-x-0 shadow-elevated" : "-translate-x-full"
        } ${collapsed ? "md:w-[72px]" : "md:w-[272px]"}`}
      >
        <div className="flex items-center gap-2.5 px-4 pb-4 pt-5">
          <BrandMark />
          {!collapsed && (
            <div className="min-w-0">
              <h1 className="truncate font-display text-[15px] font-semibold leading-tight text-ink-primary">
                Knowledge Graph
              </h1>
              <span className="text-[11px] uppercase tracking-wide text-ink-tertiary">
                Learning Assistant
              </span>
            </div>
          )}
          <button
            onClick={() => setCollapsed((v) => !v)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="ml-auto hidden h-6 w-6 flex-shrink-0 items-center justify-center rounded-md text-ink-tertiary hover:bg-hoverbg hover:text-ink-primary md:flex"
          >
            {collapsed ? "»" : "«"}
          </button>
        </div>

        <div className="px-3 pb-3.5">
          <button
            onClick={onNewChat}
            title="New Chat"
            className={`btn-primary flex w-full items-center justify-center gap-2 ${
              collapsed ? "!px-0" : ""
            }`}
          >
            <span aria-hidden="true">+</span>
            {!collapsed && "New Chat"}
          </button>
        </div>

        <div className="flex flex-col gap-0.5 px-2 pb-2.5">
          <button
            onClick={() => onChangeView("dashboard")}
            title="Progress Dashboard"
            className={`flex w-full items-center gap-2.5 rounded-md px-2.5 py-2.5 text-left text-[13.5px] font-medium transition-colors ${
              collapsed ? "justify-center" : ""
            } ${
              activeView === "dashboard"
                ? "bg-teal-dim text-teal"
                : "text-ink-secondary hover:bg-hoverbg hover:text-ink-primary"
            }`}
          >
            <span aria-hidden="true">▦</span>
            {!collapsed && "Progress Dashboard"}
          </button>
          <button
            onClick={() => onChangeView("bookmarks")}
            title="Bookmarks"
            className={`flex w-full items-center gap-2.5 rounded-md px-2.5 py-2.5 text-left text-[13.5px] font-medium transition-colors ${
              collapsed ? "justify-center" : ""
            } ${
              activeView === "bookmarks"
                ? "bg-teal-dim text-teal"
                : "text-ink-secondary hover:bg-hoverbg hover:text-ink-primary"
            }`}
          >
            <span aria-hidden="true">★</span>
            {!collapsed && "Bookmarks"}
          </button>
        </div>

        {!collapsed && (
          <div className="px-4 pb-2 pt-1 text-[11px] font-semibold uppercase tracking-wide text-ink-tertiary">
            Recent Chats
          </div>
        )}
        <div className="flex-1 overflow-y-auto overflow-x-hidden px-2">
          {!collapsed && (
            <HistoryList
              conversations={conversations}
              activeConversationId={activeConversationId}
              onSelectConversation={onSelectConversation}
              onRenameConversation={onRenameConversation}
              onDeleteConversation={onDeleteConversation}
            />
          )}
        </div>

        <div className="border-t border-border-subtle p-3">
          {!collapsed && user && (
            <UsageIndicator
              onUpgradeClick={() => setPricingOpen(true)}
              refreshKey={usageRefreshKey}
            />
          )}
          {collapsed ? (
            <button
              onClick={() => setCollapsed(false)}
              className="mx-auto flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-violet to-[#5c53c9] text-xs font-bold text-white"
              title={user ? user.email : "Sign in"}
            >
              {user ? (user.full_name || user.email).charAt(0).toUpperCase() : "?"}
            </button>
          ) : user ? (
            <AccountMenu user={user} onSignOut={onSignOut} />
          ) : (
            <Link
              href="/login"
              className="btn-ghost flex w-full items-center justify-center"
            >
              Sign In / Sign Up
            </Link>
          )}
        </div>
      </aside>
      <PricingModal isOpen={pricingOpen} onClose={() => setPricingOpen(false)} />
    </>
  );
}
