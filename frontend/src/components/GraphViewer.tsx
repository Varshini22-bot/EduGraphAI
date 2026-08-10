"use client";

import { useMemo, useState } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  Node,
  Edge,
  NodeProps,
  Handle,
  Position,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { GraphResponse } from "@/lib/types";

interface GraphViewerProps {
  graph: GraphResponse;
}

// nodeTypes map is a module-scope constant (not re-created per render) to
// avoid React Flow's "new nodeTypes/edgeTypes object" warning.
const FOCUS_NODE_TYPE = "focusTopic";
const PREREQ_NODE_TYPE = "prereqTopic";
const SUBJECT_NODE_TYPE = "subjectTopic";
const RELATED_NODE_TYPE = "relatedTopic";

const RELATION_COLORS: Record<string, string> = {
  PREREQUISITE: "#f0b457",
  HAS_TOPIC: "#8b7ff0",
  USES: "#45d6c6",
};

function edgeColor(relation: string): string {
  return RELATION_COLORS[relation] ?? "#343b4d";
}

const DEFAULT_VISIBLE_RELATED = 6;

function FocusTopicNode({ data }: NodeProps<{ label: string }>) {
  return (
    <div className="flex min-w-[130px] flex-col items-center gap-0.5 rounded-full border-2 border-teal bg-gradient-to-br from-teal-dim to-elevated px-5 py-3 text-center shadow-[0_0_0_5px_rgba(69,214,198,0.1),0_8px_20px_rgba(0,0,0,0.4)]">
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="target" position={Position.Bottom} className="opacity-0" />
      <span className="font-mono text-[9px] font-semibold uppercase tracking-wider text-teal">
        Current Topic
      </span>
      <span className="whitespace-nowrap font-display text-[14px] font-bold text-ink-primary">
        {data.label}
      </span>
      <Handle type="source" position={Position.Top} id="top" className="opacity-0" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="opacity-0" />
      <Handle type="source" position={Position.Left} className="opacity-0" />
      <Handle type="source" position={Position.Right} className="opacity-0" />
    </div>
  );
}

function SubjectTopicNode({ data }: NodeProps<{ label: string }>) {
  return (
    <div className="flex items-center gap-1.5 whitespace-nowrap rounded-lg border border-violet/70 bg-violet-dim px-3 py-1.5 text-[11.5px] font-semibold text-ink-primary">
      <Handle type="target" position={Position.Bottom} className="opacity-0" />
      <span className="font-mono text-[8.5px] uppercase tracking-wider text-violet">Subject</span>
      {data.label}
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
}

function PrereqTopicNode({ data }: NodeProps<{ label: string }>) {
  return (
    <div className="flex items-center gap-1.5 whitespace-nowrap rounded-full border border-amber bg-elevated px-3 py-1.5 text-[12px] font-semibold text-ink-primary transition-transform hover:-translate-y-0.5">
      <Handle type="target" position={Position.Bottom} className="opacity-0" />
      <span className="h-1.5 w-1.5 flex-shrink-0 rounded-full bg-amber" aria-hidden="true" />
      {data.label}
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
}

function RelatedTopicNode({ data }: NodeProps<{ label: string }>) {
  return (
    <div className="flex items-center gap-1.5 whitespace-nowrap rounded-full border border-violet bg-elevated px-3 py-1.5 text-[12px] font-semibold text-ink-primary transition-transform hover:-translate-y-0.5">
      <Handle type="target" position={Position.Left} className="opacity-0" />
      <Handle type="target" position={Position.Right} className="opacity-0" />
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <span className="h-1.5 w-1.5 flex-shrink-0 rounded-full bg-violet" aria-hidden="true" />
      {data.label}
      <Handle type="source" position={Position.Left} className="opacity-0" />
      <Handle type="source" position={Position.Right} className="opacity-0" />
      <Handle type="source" position={Position.Top} className="opacity-0" />
    </div>
  );
}

const nodeTypes = {
  [FOCUS_NODE_TYPE]: FocusTopicNode,
  [PREREQ_NODE_TYPE]: PrereqTopicNode,
  [SUBJECT_NODE_TYPE]: SubjectTopicNode,
  [RELATED_NODE_TYPE]: RelatedTopicNode,
};

type NodeRole = "prerequisite" | "subject" | "related";

function classifyRole(relation: string): NodeRole {
  if (relation === "PREREQUISITE") return "prerequisite";
  if (relation === "HAS_TOPIC") return "subject";
  return "related";
}

/**
 * Deterministic hierarchical/radial layout — NOT random positioning:
 *   - Focus (current topic) is always centered.
 *   - Subject/category nodes (HAS_TOPIC) sit directly above the topic.
 *   - Prerequisite nodes sit further above, in their own outer band.
 *   - Everything else (related concepts) is distributed across the
 *     remaining ~260° arc (left, right, and bottom), never competing
 *     with the reserved top band, so labels don't collide with the
 *     subject/prerequisite nodes above.
 */
function layoutGraph(
  graph: GraphResponse,
  maxRelated: number
): { nodes: Node[]; edges: Edge[]; hiddenRelatedCount: number } {
  const focusId = graph.nodes[0]?.id;

  const roleByNodeId = new Map<string, NodeRole>();
  for (const link of graph.links) {
    const otherId = link.source === focusId ? link.target : link.source;
    if (otherId === focusId) continue;
    const role = classifyRole(link.label);
    // A node could theoretically be reached via more than one relation;
    // prerequisite/subject take priority over a generic "related" tag.
    const existing = roleByNodeId.get(otherId);
    if (!existing || existing === "related") {
      roleByNodeId.set(otherId, role);
    }
  }

  const others = graph.nodes.slice(1);
  const prereqNodes = others.filter((n) => roleByNodeId.get(n.id) === "prerequisite");
  const subjectNodes = others.filter((n) => roleByNodeId.get(n.id) === "subject");
  const allRelatedNodes = others.filter(
    (n) => (roleByNodeId.get(n.id) ?? "related") === "related"
  );

  const hiddenRelatedCount = Math.max(0, allRelatedNodes.length - maxRelated);
  const relatedNodes = allRelatedNodes.slice(0, maxRelated);

  const visibleIds = new Set([
    focusId,
    ...prereqNodes.map((n) => n.id),
    ...subjectNodes.map((n) => n.id),
    ...relatedNodes.map((n) => n.id),
  ]);

  const nodes: Node[] = [];

  if (graph.nodes[0]) {
    nodes.push({
      id: focusId!,
      type: FOCUS_NODE_TYPE,
      position: { x: 0, y: 0 },
      data: { label: graph.nodes[0].label },
      draggable: true,
    });
  }

  // Prerequisites: outer top band, spread horizontally.
  prereqNodes.forEach((node, i) => {
    const spread = prereqNodes.length > 1 ? (i - (prereqNodes.length - 1) / 2) * 150 : 0;
    nodes.push({
      id: node.id,
      type: PREREQ_NODE_TYPE,
      position: { x: spread, y: -230 },
      data: { label: node.label },
      draggable: true,
    });
  });

  // Subject/category: inner top band, between prerequisites and the topic.
  subjectNodes.forEach((node, i) => {
    const spread = subjectNodes.length > 1 ? (i - (subjectNodes.length - 1) / 2) * 140 : 0;
    nodes.push({
      id: node.id,
      type: SUBJECT_NODE_TYPE,
      position: { x: spread, y: -120 },
      data: { label: node.label },
      draggable: true,
    });
  });

  // Related concepts: distributed across the remaining ~260° arc (left,
  // right, bottom) so they never overlap the reserved top band.
  const relatedCount = relatedNodes.length;
  relatedNodes.forEach((node, i) => {
    const startAngle = (50 * Math.PI) / 180; // just past top-right reserved zone
    const endAngle = (2 * Math.PI) - startAngle; // wrap back to just past top-left
    const angle =
      relatedCount === 1
        ? Math.PI / 2 // straight down if there's only one
        : startAngle + ((endAngle - startAngle) * i) / (relatedCount - 1);
    const radius = 190;
    nodes.push({
      id: node.id,
      type: RELATED_NODE_TYPE,
      position: { x: radius * Math.cos(angle), y: radius * Math.sin(angle) },
      data: { label: node.label },
      draggable: true,
    });
  });

  const manyEdges = graph.links.length > 10;

  const edges: Edge[] = graph.links
    .filter((link) => visibleIds.has(link.source) && visibleIds.has(link.target))
    .map((link, index) => {
      const color = edgeColor(link.label);
      // Decluttering: with many relationships, drop text labels entirely
      // rather than let them overlap — color coding still conveys relation
      // type via the legend.
      const label = manyEdges
        ? undefined
        : link.label.length > 14
        ? `${link.label.slice(0, 12)}…`
        : link.label;

      return {
        id: `${link.source}-${link.target}-${index}`,
        source: link.source,
        target: link.target,
        label,
        labelStyle: { fill: "#9ba3b4", fontSize: 9, fontWeight: 600 },
        labelBgStyle: { fill: "#1b1f2a", fillOpacity: 0.9 },
        labelBgPadding: [5, 2] as [number, number],
        labelBgBorderRadius: 5,
        style: { stroke: color, strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color, width: 13, height: 13 },
      };
    });

  return { nodes, edges, hiddenRelatedCount };
}

function canvasHeight(nodeCount: number): string {
  // Spec target: ~450-650px on desktop for the expanded interactive view —
  // this is deliberately larger than a "preview," since the expanded view
  // is opened intentionally, not shown by default on every message.
  if (nodeCount <= 4) return "450px";
  if (nodeCount <= 9) return "550px";
  return "650px";
}

// ---------------------------------------------------------------------------
// Compact preview: a short textual summary + "Open Interactive Graph"
// button. This is what renders by default per answer, so asking several
// questions in one conversation does not stack multiple full graph canvases
// down the page. The full interactive graph only mounts once expanded.
// ---------------------------------------------------------------------------
function GraphPreview({
  graph,
  onExpand,
}: {
  graph: GraphResponse;
  onExpand: () => void;
}) {
  const focusId = graph.nodes[0]?.id;
  const previewLinks = graph.links.slice(0, 3);

  return (
    <div className="rounded-xl border border-border-subtle bg-elevated/50 px-4 py-3.5">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-tertiary">
        Knowledge graph
      </div>
      <div className="flex flex-col gap-1">
        {previewLinks.map((link, i) => {
          const other = link.source === focusId ? link.target : link.source;
          const arrow = link.source === focusId ? "→" : "←";
          return (
            <div key={i} className="truncate text-[12.5px] text-ink-secondary">
              <span className="text-ink-primary">{focusId}</span>{" "}
              <span className="text-ink-tertiary">
                {arrow} <span className="font-mono text-[10px]">{link.label}</span> {arrow}
              </span>{" "}
              <span className="text-ink-primary">{other}</span>
            </div>
          );
        })}
        {graph.links.length > previewLinks.length && (
          <div className="text-[11.5px] text-ink-tertiary">
            +{graph.links.length - previewLinks.length} more relationship
            {graph.links.length - previewLinks.length === 1 ? "" : "s"}
          </div>
        )}
      </div>
      <button
        onClick={onExpand}
        className="mt-3 rounded-lg border border-teal/40 bg-teal-dim px-3 py-1.5 text-[12px] font-semibold text-teal transition-colors hover:bg-teal/20"
      >
        Open Interactive Graph ↗
      </button>
    </div>
  );
}

export default function GraphViewer({ graph }: GraphViewerProps) {
  const [expanded, setExpanded] = useState(false);
  const [showAllRelated, setShowAllRelated] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const maxRelated = showAllRelated ? Infinity : DEFAULT_VISIBLE_RELATED;
  const { nodes: rawNodes, edges, hiddenRelatedCount } = useMemo(
    () => layoutGraph(graph, maxRelated),
    [graph, maxRelated]
  );
  const graphKey = useMemo(
    () => `${graph.nodes.map((n) => n.id).join("|")}-${showAllRelated}`,
    [graph, showAllRelated]
  );

  // Search dims non-matching nodes rather than removing them, so the graph
  // shape/context stays visible while the match is highlighted.
  const nodes = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) return rawNodes;
    return rawNodes.map((node) => {
      const label = (node.data as { label: string }).label.toLowerCase();
      const isMatch = label.includes(term);
      return { ...node, style: { ...node.style, opacity: isMatch ? 1 : 0.25 } };
    });
  }, [rawNodes, searchTerm]);

  if (graph.nodes.length === 0) return null;

  if (!expanded) {
    return <GraphPreview graph={graph} onExpand={() => setExpanded(true)} />;
  }

  const height = fullscreen ? "calc(100vh - 140px)" : canvasHeight(nodes.length);

  return (
    <div
      className={
        fullscreen
          ? "fixed inset-0 z-[160] flex flex-col bg-base p-4 animate-fadein"
          : "animate-fadein"
      }
      aria-label="Knowledge graph"
    >
      <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="text-[12px] font-semibold uppercase tracking-wide text-ink-tertiary">
            Interactive Knowledge Graph
          </div>
          {!fullscreen && (
            <button
              onClick={() => setExpanded(false)}
              className="text-[11px] text-ink-tertiary underline hover:text-ink-primary"
            >
              Collapse
            </button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search nodes..."
            className="w-32 rounded-md border border-border-subtle bg-inputbg px-2.5 py-1 text-[11.5px] text-ink-primary outline-none focus:border-teal sm:w-40"
          />
          <button
            onClick={() => setFullscreen((v) => !v)}
            title={fullscreen ? "Exit fullscreen" : "Fullscreen"}
            className="rounded-md border border-border-subtle px-2 py-1 text-[11px] text-ink-secondary hover:border-teal hover:text-teal"
          >
            {fullscreen ? "⤡ Exit" : "⤢ Fullscreen"}
          </button>
          <div className="hidden items-center gap-3 text-[11px] text-ink-tertiary md:flex">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-teal" /> Current
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-violet" /> Related / Subject
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-amber" /> Prerequisite
            </span>
          </div>
        </div>
      </div>

      {hiddenRelatedCount > 0 && (
        <button
          onClick={() => setShowAllRelated(true)}
          className="mb-2.5 rounded-full border border-border-subtle bg-elevated px-3 py-1.5 text-[11.5px] font-medium text-ink-secondary transition-colors hover:border-teal hover:text-ink-primary"
        >
          Show {hiddenRelatedCount} more connection{hiddenRelatedCount === 1 ? "" : "s"}
        </button>
      )}

      <div
        className={`relative w-full overflow-hidden rounded-xl border border-border-subtle bg-base ${
          fullscreen ? "flex-1" : ""
        }`}
        style={fullscreen ? undefined : { height }}
      >
        <ReactFlow
          key={graphKey}
          className="h-full w-full"
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2, duration: 300, maxZoom: 1.3 }}
          minZoom={0.3}
          maxZoom={1.75}
          proOptions={{ hideAttribution: true }}
        >
          <Background variant={BackgroundVariant.Dots} gap={18} size={1} color="#232838" />
          <Controls showInteractive={false} />
          {nodes.length > 6 && (
            <MiniMap
              pannable
              zoomable
              maskColor="rgba(10, 13, 19, 0.75)"
              nodeColor={(node) =>
                node.type === FOCUS_NODE_TYPE
                  ? "#45d6c6"
                  : node.type === PREREQ_NODE_TYPE
                  ? "#f0b457"
                  : "#8b7ff0"
              }
              style={{ background: "#12151d" }}
            />
          )}
        </ReactFlow>
      </div>
    </div>
  );
}
