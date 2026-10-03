"use client";

import { useEffect, useRef } from "react";
import { GraphResponse } from "@/lib/types";
import GraphViewer from "@/components/GraphViewer";

interface GraphModalProps {
  isOpen: boolean;
  onClose: () => void;
  topic: string;
  graph: GraphResponse | null;
  isLoading?: boolean;
}

export default function GraphModal({
  isOpen,
  onClose,
  topic,
  graph,
  isLoading = false,
}: GraphModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/70 p-3 sm:p-6 backdrop-blur-sm animate-fadein"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="graph-modal-title"
        onClick={(e) => e.stopPropagation()}
        className="card flex h-[85vh] w-full max-w-5xl flex-col overflow-hidden p-0 shadow-elevated focus:outline-none"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border-subtle bg-elevated/70 px-5 py-3.5">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-lg">🕸️</span>
              <h2
                id="graph-modal-title"
                className="truncate font-display text-[16px] font-bold text-ink-primary sm:text-[18px]"
              >
                Knowledge Graph: {topic}
              </h2>
            </div>
            <p className="mt-0.5 text-[12px] text-ink-secondary">
              Grounded concept hierarchy, prerequisite links, and curriculum connections
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close knowledge graph modal"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
          >
            ✕
          </button>
        </div>

        {/* Graph Body */}
        <div className="relative flex-1 bg-base">
          {isLoading ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 text-ink-secondary">
              <span className="h-8 w-8 animate-spin rounded-full border-2 border-teal/20 border-t-teal" />
              <p className="text-[13.5px] font-medium">
                Traversing Neo4j knowledge graph for &quot;{topic}&quot;...
              </p>
            </div>
          ) : graph && graph.nodes.length > 0 ? (
            <div className="h-full w-full">
              <GraphViewer graph={graph} />
            </div>
          ) : (
            <div className="flex h-full flex-col items-center justify-center p-6 text-center text-ink-secondary">
              <span className="mb-2 text-3xl">🌲</span>
              <p className="text-[14px] font-medium text-ink-primary">
                No direct graph relationships mapped for &quot;{topic}&quot;
              </p>
              <p className="mt-1 max-w-[360px] text-[12.5px] text-ink-tertiary">
                This topic was answered using broader syllabus context. Try asking for a
                core concept like &quot;Quick Sort&quot;, &quot;Binary Search&quot;, or &quot;Dijkstra&quot;.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
