"use client";

import { useMemo, useState } from "react";
import { ChatMessage as ChatMessageType, GraphResponse } from "@/lib/types";
import { useSettings } from "@/context/SettingsContext";
import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";
import ResponseActions from "./ResponseActions";
import AnswerCard from "@/components/AnswerCard";
import RelatedTopics from "@/components/RelatedTopics";
import LearningPath from "@/components/LearningPath";
import Recommendations from "@/components/Recommendations";
import GraphViewer from "@/components/GraphViewer";

interface ChatMessageProps {
  message: ChatMessageType;
  isAskPending: boolean;
  onSelectTopic: (topic: string) => void;
  onRetryAsk: (messageId: string, query: string) => void;
  onDismissAskError?: (messageId: string) => void;
  onRetryGraph: (messageId: string, query: string) => void;
  onRegenerate: (messageId: string, query: string) => void;
  onEditQuery?: (query: string) => void;
  onShareConversation?: () => void;
  onOpenGraphModal?: (message: ChatMessageType) => void;
  isBookmarked: boolean;
  onToggleBookmark: (topic: string, answer: string) => void;
}

function sanitizeErrorMessage(raw: string): string {
  if (!raw) return "Something went wrong. Please try again.";
  if (/neo4j|bolt:\/\/|render\.com|password|credential|traceback|line \d+|syntaxerror/i.test(raw)) {
    return "Something went wrong while retrieving knowledge graph data. Please try again.";
  }
  return raw;
}

function ErrorBanner({
  message,
  onRetry,
  onDismiss,
}: {
  message: string;
  onRetry: () => void;
  onDismiss?: () => void;
}) {
  const safeMessage = sanitizeErrorMessage(message);

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 self-start rounded-xl border border-danger/40 bg-danger-dim/50 px-4 py-3 text-[13px] text-ink-primary shadow-sm animate-fadein">
      <div className="flex items-center gap-2.5 min-w-0">
        <span className="flex-shrink-0 text-danger text-base" aria-hidden="true">
          ⚠️
        </span>
        <span className="font-medium text-danger-text">{safeMessage}</span>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onRetry}
          className="rounded-md bg-danger px-3 py-1 text-xs font-semibold text-white transition-opacity hover:opacity-90"
        >
          Retry
        </button>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="rounded-md border border-border-subtle bg-elevated px-2.5 py-1 text-xs font-medium text-ink-secondary hover:text-ink-primary"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}

function SectionDivider() {
  return <div className="h-px w-full bg-border-subtle" />;
}

function filterGraphByDirection(
  graph: GraphResponse,
  showOutgoing: boolean,
  showIncoming: boolean
): GraphResponse {
  if (showOutgoing && showIncoming) return graph;
  const focusId = graph.nodes[0]?.id;
  if (!focusId) return graph;

  const links = graph.links.filter((link) => {
    const isOutgoing = link.source === focusId;
    const isIncoming = link.target === focusId;
    if (isOutgoing) return showOutgoing;
    if (isIncoming) return showIncoming;
    return true;
  });

  const referencedIds = new Set(links.flatMap((l) => [l.source, l.target]));
  const nodes = graph.nodes.filter(
    (node) => node.id === focusId || referencedIds.has(node.id)
  );

  return { nodes, links };
}

export default function ChatMessage({
  message,
  isAskPending,
  onSelectTopic,
  onRetryAsk,
  onDismissAskError,
  onRetryGraph,
  onRegenerate,
  onEditQuery,
  onShareConversation,
  onOpenGraphModal,
  isBookmarked,
  onToggleBookmark,
}: ChatMessageProps) {
  const { settings } = useSettings();
  const [retrievedConceptsOpen, setRetrievedConceptsOpen] = useState(false);

  const visibleGraph = useMemo(() => {
    if (!message.graph) return null;
    return filterGraphByDirection(
      message.graph,
      settings.showOutgoingRelationships,
      settings.showIncomingRelationships
    );
  }, [message.graph, settings.showOutgoingRelationships, settings.showIncomingRelationships]);

  const showRelatedTopicsSection =
    settings.showGraphContext && settings.showRelatedTopics;

  const hasAnySecondaryContent =
    (showRelatedTopicsSection && message.response
      ? message.response.graph_context.length > 0
      : false) ||
    (settings.showLearningPath && message.response
      ? message.response.learning_path.length > 0
      : false) ||
    (settings.showRecommendations && message.response
      ? message.response.recommendations.length > 0
      : false);

  const showGraphSection = settings.showGraphContext;

  return (
    <div className="chat-message-gap flex flex-col gap-4">
      {/* User Message Bubble with Edit Button */}
      <div className="group flex flex-col items-end gap-1">
        <ChatBubble role="user">{message.query}</ChatBubble>
        {onEditQuery && (
          <button
            onClick={() => onEditQuery(message.query)}
            title="Edit and resend this question"
            className="flex items-center gap-1 pr-1 text-[11px] text-ink-tertiary opacity-0 transition-opacity hover:text-ink-primary group-hover:opacity-100"
          >
            <span>✎</span>
            <span>Edit</span>
          </button>
        )}
      </div>

      {isAskPending && (
        <div className="flex flex-col gap-2">
          <TypingIndicator label="Grounding answer with EduGraphAI Knowledge Graph..." />
          <div className="flex items-center gap-2 pl-3 text-[11.5px] text-ink-tertiary">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-teal" />
            <span>Searching curriculum nodes, prerequisite hierarchies & syllabus connections...</span>
          </div>
        </div>
      )}

      {message.askError && (
        <ErrorBanner
          message={message.askError}
          onRetry={() => onRetryAsk(message.id, message.query)}
          onDismiss={() => onDismissAskError?.(message.id)}
        />
      )}

      {message.response && (
        <ChatBubble role="assistant">
          <div className="chat-answer-gap flex flex-col gap-4">
            {/* Phase 5: Knowledge Graph Grounding Badge & Graph Modal Trigger */}
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle/50 pb-2.5">
              <div className="flex items-center gap-1.5 rounded-full bg-teal-dim/60 px-2.5 py-0.5 text-[11px] font-semibold text-teal">
                <span className="flex h-3.5 w-3.5 items-center justify-center rounded-full bg-teal text-[9px] font-bold text-[#05221f]">
                  ✓
                </span>
                <span>Knowledge Graph Grounded</span>
              </div>

              {onOpenGraphModal && (message.graph || message.response.topic) && (
                <button
                  type="button"
                  onClick={() => onOpenGraphModal(message)}
                  className="flex items-center gap-1.5 rounded-md border border-border-subtle bg-elevated px-2.5 py-1 text-[11.5px] font-medium text-ink-secondary transition-colors hover:border-teal hover:text-teal"
                  title="Explore concept relationships in interactive visual graph"
                >
                  <span>🕸️</span>
                  <span>View Knowledge Graph</span>
                </button>
              )}
            </div>

            {/* Answer Content */}
            <AnswerCard
              topic={message.response.topic}
              answer={message.response.answer}
              answerStyle={settings.answerStyle}
              learningLevel={settings.learningLevel}
            />

            {/* Collapsible Retrieved Concepts (Phase 5) */}
            {message.response.graph_context && message.response.graph_context.length > 0 && (
              <div className="rounded-xl border border-border-subtle/70 bg-elevated/40 p-3">
                <button
                  type="button"
                  onClick={() => setRetrievedConceptsOpen(!retrievedConceptsOpen)}
                  className="flex w-full items-center justify-between text-left text-[12px] font-medium text-ink-secondary hover:text-ink-primary"
                >
                  <span className="flex items-center gap-2">
                    <span className="text-[10px] text-teal">
                      {retrievedConceptsOpen ? "▼" : "▶"}
                    </span>
                    <span>View retrieved concepts ({message.response.graph_context.length})</span>
                  </span>
                  <span className="font-mono text-[10.5px] text-ink-tertiary">Neo4j Context</span>
                </button>

                {retrievedConceptsOpen && (
                  <div className="mt-2.5 border-t border-border-subtle/50 pt-2.5 animate-fadein">
                    <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-ink-tertiary">
                      Knowledge Graph Context
                    </div>
                    <ul className="grid grid-cols-1 gap-1.5 sm:grid-cols-2 text-[12px]">
                      {message.response.graph_context.map((item, idx) => (
                        <li
                          key={idx}
                          className="flex items-center gap-2 rounded-md bg-elevated/80 px-2 py-1 text-ink-secondary"
                        >
                          <span className="h-1.5 w-1.5 flex-shrink-0 rounded-full bg-teal" />
                          <span className="truncate font-medium text-ink-primary">{item.related}</span>
                          {item.relation && (
                            <span className="ml-auto text-[10px] text-ink-tertiary uppercase">
                              {item.relation}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Response Toolbar & Educational Action Chips */}
            <ResponseActions
              answerText={message.response.answer}
              topic={message.response.topic}
              originalQuery={message.query}
              isBookmarked={isBookmarked}
              onToggleBookmark={() =>
                onToggleBookmark(message.response!.topic, message.response!.answer)
              }
              onRegenerate={() => onRegenerate(message.id, message.query)}
              onSelectTopic={onSelectTopic}
              onShare={onShareConversation}
            />

            {hasAnySecondaryContent && <SectionDivider />}

            {showRelatedTopicsSection && (
              <RelatedTopics
                items={message.response.graph_context}
                onSelectTopic={onSelectTopic}
              />
            )}
            {settings.showLearningPath && (
              <LearningPath steps={message.response.learning_path} />
            )}
            {settings.showRecommendations && (
              <Recommendations
                topics={message.response.recommendations}
                onSelectTopic={onSelectTopic}
              />
            )}

            {showGraphSection &&
              (message.isGraphLoading || message.graphError || visibleGraph) && (
                <SectionDivider />
              )}

            {showGraphSection && message.isGraphLoading && (
              <TypingIndicator label="Mapping the knowledge graph..." />
            )}

            {showGraphSection && message.graphError && (
              <ErrorBanner
                message={message.graphError}
                onRetry={() => onRetryGraph(message.id, message.query)}
              />
            )}

            {showGraphSection && visibleGraph && <GraphViewer graph={visibleGraph} />}
          </div>
        </ChatBubble>
      )}
    </div>
  );
}
