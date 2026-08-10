"use client";

interface NavbarProps {
  title: string;
  subtitle?: string;
  onOpenSidebar: () => void;
  showBookmarkAction: boolean;
  isBookmarked: boolean;
  onToggleBookmark: () => void;
}

export default function Navbar({
  title,
  subtitle,
  onOpenSidebar,
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
      </div>
    </header>
  );
}
