// ---------------------------------------------------------------------------
// Backend response shapes — these mirror the FastAPI backend exactly.
// Do not change these without checking the backend contract first.
// ---------------------------------------------------------------------------

export interface GraphContextItem {
  relation: string;
  related: string;
}

export interface AskResponse {
  query: string;
  topic: string;
  answer: string;
  graph_context: GraphContextItem[];
  learning_path: string[];
  recommendations: string[];
}

export interface GraphNodeData {
  id: string;
  label: string;
  // Additive — populated from the backend's target_type/target_subject/
  // source_type/source_subject where available. Optional so GraphViewer.tsx
  // (which only reads id/label today) needed no changes.
  type?: string;
  subject?: string;
}

export interface GraphLinkData {
  source: string;
  target: string;
  // GraphViewer.tsx reads `label` for edge display/coloring — kept as the
  // primary field so it stays untouched. `relationship` carries the same
  // value under the name used elsewhere in the verified contract, for
  // consistency ahead of the Neo4j phase.
  label: string;
  relationship?: string;
}

export interface GraphResponse {
  nodes: GraphNodeData[];
  links: GraphLinkData[];
}

// The backend only guarantees "knowledge graph statistics" here, without a
// fixed field list, so every field is optional and the UI falls back
// gracefully (see ProgressDashboard.tsx) if a field is missing.
export interface StatsResponse {
  total_searches?: number;
  topics_learned?: number;
  total_nodes?: number;
  total_relationships?: number;
  most_recent_topic?: string;
  [key: string]: unknown;
}

// ---------------------------------------------------------------------------
// Frontend-only UI types
// ---------------------------------------------------------------------------

export interface ChatMessage {
  id: string;
  query: string;
  timestamp: string;
  response: AskResponse | null;
  graph: GraphResponse | null;
  isGraphLoading: boolean;
  askError: string | null;
  graphError: string | null;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
  pinned?: boolean;
  archived?: boolean;
}

export interface Bookmark {
  id: string;
  topic: string;
  answerSnippet: string;
  savedAt: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export type AuthMode = "login" | "signup";

// ---------------------------------------------------------------------------
// Dashboard metrics — all derived client-side from conversations/bookmarks
// already in state (per "for now calculate from frontend data").
// ---------------------------------------------------------------------------

export interface SubjectProgress {
  subject: string;
  topicsExplored: number;
  percent: number;
}

export interface DashboardMetrics {
  totalQuestions: number;
  topicsLearned: number;
  bookmarkedTopics: number;
  learningPathsCompleted: number;
  recentlyLearned: string[];
  subjects: SubjectProgress[];
}
