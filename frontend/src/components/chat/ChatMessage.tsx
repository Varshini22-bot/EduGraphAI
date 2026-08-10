import { useMemo } from "react";
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
  onRetryGraph: (messageId: string, query: string) => void;
  onRegenerate: (messageId: string, query: string) => void;
  isBookmarked: boolean;
  onToggleBookmark: (topic: string, answer: string) => void;
}

function ErrorBanner({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="flex items-center gap-3 self-start rounded-lg border border-danger/35 bg-danger-dim px-3.5 py-3 text-[13px] text-ink-primary animate-fadein">
      <span className="flex-shrink-0 text-danger" aria-hidden="true">
        ⚠
      </span>
      <span className="flex-1 leading-relaxed">{message}</span>
      <button
        onClick={onRetry}
        className="flex-shrink-0 rounded-md border border-danger px-3 py-1.5 text-xs font-semibold text-danger transition-colors hover:bg-danger-dim"
      >
        Retry
      </button>
    </div>
  );
}

// A subtle rule between answer sections — replaces the old separate
// bordered "card" per section, so the whole response reads as one
// continuous, conversational answer instead of a stack of dashboard tiles.
function SectionDivider() {
  return <div className="h-px w-full bg-border-subtle" />;
}

/**
 * Filters a graph's links (and any nodes that become orphaned as a result)
 * by relationship direction relative to the focus node (graph.nodes[0]),
 * per showIncomingRelationships/showOutgoingRelationships. Outgoing links
 * have the focus node as `source`; incoming links have it as `target` —
 * this mirrors exactly how getGraph() in api.ts builds them.
 */
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
  onRetryGraph,
  onRegenerate,
  isBookmarked,
  onToggleBookmark,
}: ChatMessageProps) {
  const { settings } = useSettings();

  const visibleGraph = useMemo(() => {
    if (!message.graph) return null;
    return filterGraphByDirection(
      message.graph,
      settings.showOutgoingRelationships,
      settings.showIncomingRelationships
    );
  }, [message.graph, settings.showOutgoingRelationships, settings.showIncomingRelationships]);

  // "Show related topics" gates the same graph_context chips as Learning
  // Preferences' "Show graph context" toggle — there is only one such
  // component in this app, so both settings gate it together (AND) rather
  // than pretending they control two separate features that don't exist.
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
      <ChatBubble role="user">{message.query}</ChatBubble>

      {isAskPending && <TypingIndicator label="Thinking..." />}

      {message.askError && (
        <ErrorBanner
          message={message.askError}
          onRetry={() => onRetryAsk(message.id, message.query)}
        />
      )}

      {message.response && (
        <ChatBubble role="assistant">
          <div className="chat-answer-gap flex flex-col gap-5">
            <AnswerCard
              topic={message.response.topic}
              answer={message.response.answer}
              answerStyle={settings.answerStyle}
              learningLevel={settings.learningLevel}
            />

            <ResponseActions
              answerText={message.response.answer}
              topic={message.response.topic}
              isBookmarked={isBookmarked}
              onToggleBookmark={() =>
                onToggleBookmark(message.response!.topic, message.response!.answer)
              }
              onRegenerate={() => onRegenerate(message.id, message.query)}
              onSelectTopic={onSelectTopic}
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
