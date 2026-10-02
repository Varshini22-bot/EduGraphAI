"use client";

interface NavbarProps {
  title: string;
  subtitle?: string;
  onOpenSidebar: () => void;
  onShare?: () => void;
  showBookmarkAction: boolean;
  isBookmarked: boolean;
  onToggleBookmark: () => void;
}

function ShareIcon({ className }: { className?: string }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className ?? "flex-shrink-0"}
    >
      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
      <polyline points="16 6 12 2 8 6" />
      <line x1="12" y1="2" x2="12" y2="15" />
    </svg>
  );
}

export default function Navbar({
  title,
  subtitle,
  onOpenSidebar,
  onShare,
  showBookmarkAction,
  isBookmarked,
  onToggleBookmark,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-20 flex h-[60px] items-center justify-between border-b border-border-subtle bg-base/85 px-5 backdrop-blur-sm">
      <div className="flex min-w-0 items-center gap-3">
        <button
          onClick={onOpenSidebar}
          aria-label="Open sidebar"
          className="flex h-[34px] w-[34px] flex-shrink-0 items-center justify-center rounded-md border border-border-subtle text-ink-secondary md:hidden"
        >
          ☰
        </button>
        <div className="min-w-0">
          <div className="truncate text-[14.5px] font-semibold text-ink-primary">
            {title}
          </div>
          {subtitle && (
            <div className="text-xs text-ink-tertiary">{subtitle}</div>
          )}
        </div>
      </div>

      <div className="flex flex-shrink-0 items-center gap-2">
        {showBookmarkAction && (
          <button
            onClick={onToggleBookmark}
            aria-pressed={isBookmarked}
            aria-label="Bookmark this topic"
            title="Bookmark this topic"
            className={`flex h-[34px] w-[34px] items-center justify-center rounded-md border text-base transition-colors ${
              isBookmarked
                ? "border-amber text-amber"
                : "border-border-subtle text-ink-secondary hover:border-border-strong hover:text-ink-primary"
            }`}
          >
            {isBookmarked ? "★" : "☆"}
          </button>
        )}
        <button
          onClick={onShare}
          aria-label="Share conversation"
          title="Share conversation"
          className="flex h-[34px] items-center gap-1.5 rounded-md border border-border-subtle bg-elevated px-2.5 text-[13px] font-medium text-ink-primary transition-colors hover:border-border-strong hover:bg-hoverbg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/50 active:scale-[0.98]"
        >
          <ShareIcon />
          <span className="hidden sm:inline">Share</span>
        </button>
      </div>
    </header>
  );
}
