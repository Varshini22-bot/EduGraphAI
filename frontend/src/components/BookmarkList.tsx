import { Bookmark } from "@/lib/types";

interface BookmarkListProps {
  bookmarks: Bookmark[];
  onOpen: (topic: string) => void;
  onRemove: (id: string) => void;
}

export default function BookmarkList({
  bookmarks,
  onOpen,
  onRemove,
}: BookmarkListProps) {
  return (
    <div className="mx-auto max-w-[820px] px-6 pb-16 pt-7">
      <h2 className="mb-1 font-display text-[22px] font-bold text-ink-primary">
        Bookmarks
      </h2>
      <p className="mb-6 text-[13.5px] text-ink-secondary">
        Topics you've saved for quick access later. Click one to reopen it.
      </p>

      {bookmarks.length === 0 ? (
        <div className="card px-5 py-10 text-center text-[13.5px] text-ink-tertiary">
          You haven't bookmarked any topics yet. Tap the star icon on an
          answer to save it here.
        </div>
      ) : (
        <div className="flex flex-col gap-2.5">
          {bookmarks.map((bookmark) => (
            <div
              key={bookmark.id}
              className="card flex items-start justify-between gap-4 px-4.5 py-4"
            >
              <button
                onClick={() => onOpen(bookmark.topic)}
                className="min-w-0 flex-1 text-left"
              >
                <div className="mb-1.5 text-[14.5px] font-semibold text-ink-primary hover:text-teal">
                  {bookmark.topic}
                </div>
                <div className="text-[13px] leading-relaxed text-ink-secondary">
                  {bookmark.answerSnippet}
                </div>
                <div className="mt-2 font-mono text-[11px] text-ink-tertiary">
                  Saved {new Date(bookmark.savedAt).toLocaleDateString()}
                </div>
              </button>
              <button
                onClick={() => onRemove(bookmark.id)}
                aria-label={`Remove ${bookmark.topic} bookmark`}
                title="Remove bookmark"
                className="flex h-[30px] w-[30px] flex-shrink-0 items-center justify-center rounded-md border border-border-subtle text-ink-tertiary transition-colors hover:border-danger hover:text-danger"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
