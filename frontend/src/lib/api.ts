import { AskResponse, GraphLinkData, GraphNodeData, GraphResponse, StatsResponse } from "./types";

// ---------------------------------------------------------------------------
// LIVE API LAYER
//
// Talks to the existing FastAPI backend via NEXT_PUBLIC_API_URL. The
// backend's actual verified routes used here:
//   GET  /ask?query=<question>            (api/routes.py)
//   GET  /graph/topic/{topic_name}          (api/graph_routes.py)
//   GET  /stats                             (api/routes.py)
// ---------------------------------------------------------------------------

export type ApiErrorKind = "config" | "network" | "http" | "parse" | "empty";

export class ApiError extends Error {
  kind: ApiErrorKind;
  status?: number;

  constructor(message: string, kind: ApiErrorKind, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
  }
}

export function getBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!baseUrl) {
    throw new ApiError(
      "NEXT_PUBLIC_API_URL is not set. Add it to .env.local (e.g. " +
        "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000) and restart the dev server.",
      "config"
    );
  }
  return baseUrl;
}

// Token key matches src/lib/auth/authClient.ts exactly — duplicated as a
// constant (not imported) to avoid a circular import (authClient could
// reasonably import from api.ts, not the reverse).
const TOKEN_KEY = "kgla_access_token";

function getAuthHeader(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Shared fetch helper: builds the URL from NEXT_PUBLIC_API_URL, and turns
 * every failure mode (backend down, network error, non-2xx status, invalid
 * JSON, empty body) into a typed ApiError with a message safe to show
 * directly in the UI.
 */
async function fetchJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}${path}`;

  let res: Response;
  try {
    res = await fetch(url, {
      method: "GET",
      ...options,
      headers: {
        Accept: "application/json",
        ...getAuthHeader(),
        ...(options.headers ?? {}),
      },
    });
  } catch {
    // fetch() throws a TypeError for DNS failures, connection refused,
    // CORS blocks, etc. — i.e. "the backend is unreachable".
    throw new ApiError(
      `Could not reach the backend at ${baseUrl}. Make sure the FastAPI ` +
        `server is running and reachable at that address.`,
      "network"
    );
  }

  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      if (body && typeof body.detail === "string") {
        detail = `: ${body.detail}`;
      }
    } catch {
      // error body wasn't JSON — ignore and use the generic message below
    }
    throw new ApiError(
      `The backend returned an error (HTTP ${res.status})${detail}`,
      "http",
      res.status
    );
  }

  let data: unknown;
  try {
    data = await res.json();
  } catch {
    throw new ApiError(
      "The backend response could not be parsed as JSON.",
      "parse"
    );
  }

  if (data === null || data === undefined) {
    throw new ApiError("The backend returned an empty response.", "empty");
  }

  return data as T;
}

// ---------------------------------------------------------------------------
// /ask
// ---------------------------------------------------------------------------

// Shape as verified from RAGService.answer() returned directly by GET /ask —
// NOT the same as the frontend's AskResponse; mapped below.
interface BackendAskResponse {
  status?: boolean;
  message?: string;
  query?: string;
  topic?: string | null;
  answer?: string | null;
  graph_context?: { relationship: string; target: string }[];
  incoming?: unknown[];
  learning_path?: string[];
  recommendations?: string[];
  error?: string;
}

/**
 * Mirrors: GET /ask?query=<question>
 *
 * The backend signals soft failure (empty query, RAG exception, topic not
 * found) via "status": false with HTTP 200, not via an HTTP error status —
 * verified directly in api/routes.py. That must be checked explicitly, or
 * the backend's real message/error text never reaches the UI.
 */
export async function askQuestion(query: string): Promise<AskResponse> {
  const data = await fetchJson<BackendAskResponse>(
    `/ask?query=${encodeURIComponent(query)}`
  );

  if (data.status === false) {
    throw new ApiError(
      data.message ?? data.error ?? "The backend could not answer this question.",
      "empty"
    );
  }

  if (!data.topic || !data.answer) {
    throw new ApiError(
      "The backend response was missing 'topic' or 'answer'.",
      "empty"
    );
  }

  return {
    query: data.query ?? query,
    topic: data.topic,
    answer: data.answer,
    // Backend field names (relationship/target) mapped onto the existing
    // frontend shape (relation/related) here at the API boundary, so
    // types.ts's GraphContextItem and RelatedTopics.tsx stay unchanged.
    // Items missing either field are dropped rather than rendered blank.
    graph_context: (data.graph_context ?? [])
      .filter((item) => item && item.relationship && item.target)
      .map((item) => ({
        relation: item.relationship,
        related: item.target,
      })),
    learning_path: data.learning_path ?? [],
    recommendations: data.recommendations ?? [],
  };
}

// ---------------------------------------------------------------------------
// /graph
// ---------------------------------------------------------------------------

interface BackendGraphRelation {
  relationship: string;
  target?: string;
  source?: string;
  target_type?: string | null;
  target_subject?: string | null;
  source_type?: string | null;
  source_subject?: string | null;
}

interface BackendGraphTopicResponse {
  status?: boolean;
  message?: string;
  node?: unknown;
  outgoing?: BackendGraphRelation[];
  incoming?: BackendGraphRelation[];
}

/**
 * Mirrors: GET /graph/topic/{topic_name}
 *
 * `topic` must be the topic string returned by askQuestion() (AskResponse.topic),
 * not the user's raw question — verified requirement, since the backend
 * route matches on an exact topic name, not a free-text query.
 *
 * Transforms the backend's { node, outgoing, incoming } shape into the
 * { nodes, links } shape GraphViewer.tsx already expects, so GraphViewer
 * itself does not need to change. The center node's id/label uses the
 * known `topic` string rather than the raw backend `node` object, since
 * that object's own property names for a display label aren't guaranteed
 * by graph_service.py (it returns the raw Neo4j node dict as-is).
 */
export async function getGraph(topic: string): Promise<GraphResponse> {
  const data = await fetchJson<BackendGraphTopicResponse>(
    `/graph/topic/${encodeURIComponent(topic)}`
  );

  if (data.status === false) {
    throw new ApiError(
      data.message ?? `No graph data found for "${topic}".`,
      "empty"
    );
  }

  const nodesById = new Map<string, GraphNodeData>();
  const links: GraphLinkData[] = [];

  nodesById.set(topic, { id: topic, label: topic });

  for (const item of data.outgoing ?? []) {
    if (!item.target) continue;
    if (!nodesById.has(item.target)) {
      nodesById.set(item.target, {
        id: item.target,
        label: item.target,
        type: item.target_type ?? undefined,
        subject: item.target_subject ?? undefined,
      });
    }
    links.push({
      source: topic,
      target: item.target,
      label: item.relationship,
      relationship: item.relationship,
    });
  }

  for (const item of data.incoming ?? []) {
    if (!item.source) continue;
    if (!nodesById.has(item.source)) {
      nodesById.set(item.source, {
        id: item.source,
        label: item.source,
        type: item.source_type ?? undefined,
        subject: item.source_subject ?? undefined,
      });
    }
    links.push({
      source: item.source,
      target: topic,
      label: item.relationship,
      relationship: item.relationship,
    });
  }

  // Dedupe links too (not just nodes) — the backend can return the same
  // relationship more than once (verified: graph_service.py's Cypher
  // queries don't dedupe), which would otherwise draw overlapping edges.
  const seenLinks = new Set<string>();
  const dedupedLinks = links.filter((link) => {
    const key = `${link.source}|${link.target}|${link.label}`;
    if (seenLinks.has(key)) return false;
    seenLinks.add(key);
    return true;
  });

  return {
    nodes: Array.from(nodesById.values()),
    links: dedupedLinks,
  };
}

/**
 * Mirrors: GET /stats — unchanged, route and usage preserved as-is.
 */
export async function getStats(): Promise<StatsResponse> {
  const data = await fetchJson<StatsResponse>("/stats");
  return data ?? {};
}

// ---------------------------------------------------------------------------
// USAGE LIMITS (new — NOT YET a real backend contract)
//
// GET /usage/me does not exist on the verified backend today. This is
// architected so the moment it's added, it works with zero other frontend
// changes — but until then, it fails soft: any error (404 because the
// route doesn't exist, network failure, etc.) returns null rather than
// throwing, and every caller treats null as "usage tracking isn't
// available" (never as "unlimited" or "blocked" — just unknown).
//
// REQUIRED BACKEND ADDITION (not implemented here — no write access to
// your backend repo):
//   GET /usage/me  (requires Authorization: Bearer <token>)
//   → { "used": number, "limit": number | null, "plan": "free" | "pro", "resets_at": string | null }
//   limit: null means unlimited (Pro). The endpoint must require auth —
//   usage is meaningless if not tied to an authenticated user — and the
//   actual enforcement (rejecting requests over the limit) MUST happen
//   in POST /ask itself (e.g. HTTP 429), not just be reported here.
//   Because askQuestion() already surfaces any non-2xx status as an
//   ApiError with the backend's message, a future 429 from /ask needs
//   NO frontend code change to display correctly.
// ---------------------------------------------------------------------------

export interface UsageInfo {
  used: number;
  limit: number | null;
  plan: "free" | "pro";
  status: "active" | "expired" | "cancelled" | "none";
  expiresAt: string | null;
  resetsAt: string | null;
}

export async function getUsage(): Promise<UsageInfo | null> {
  const baseUrl = getBaseUrl();
  try {
    const res = await fetch(`${baseUrl}/usage/me`, {
      headers: { Accept: "application/json", ...getAuthHeader() },
    });
    if (!res.ok) return null; // includes 404 — route not implemented yet
    const data = await res.json();
    if (typeof data?.used !== "number") return null;
    return {
      used: data.used,
      limit: typeof data.limit === "number" ? data.limit : null,
      plan: data.plan === "pro" ? "pro" : "free",
      status:
        data.status === "active" || data.status === "expired" || data.status === "cancelled"
          ? data.status
          : "none",
      expiresAt: typeof data.expires_at === "string" ? data.expires_at : null,
      resetsAt: typeof data.resets_at === "string" ? data.resets_at : null,
    };
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// SUBSCRIPTION CHECKOUT (new — NOT YET a real backend contract)
//
// POST /subscription/checkout does not exist on the verified backend today.
// This never claims success client-side — it only ever reports one of:
//   "not_configured" — backend reachable but Razorpay isn't set up (no
//                       RAZORPAY_KEY_ID/SECRET configured server-side)
//   "unavailable"     — the route doesn't exist yet / network failure
//   an order to hand to Razorpay's checkout widget (once implemented)
// Actual payment success is NEVER decided here — only a real backend
// verification (POST /subscription/verify, checking Razorpay's signature)
// may ever mark a subscription active. See the backend spec provided
// alongside this change for the required routes.
// ---------------------------------------------------------------------------

export type CheckoutResult =
  | { status: "not_configured" }
  | { status: "unavailable" }
  | { status: "order_created"; orderId: string; amount: number; currency: string; keyId: string };

export async function startProCheckout(): Promise<CheckoutResult> {
  const baseUrl = getBaseUrl();
  try {
    const res = await fetch(`${baseUrl}/subscription/checkout`, {
      method: "POST",
      headers: { Accept: "application/json", ...getAuthHeader() },
    });

    if (res.status === 404) return { status: "unavailable" };
    if (res.status === 503) return { status: "not_configured" };
    if (!res.ok) return { status: "unavailable" };

    const data = await res.json();
    if (!data?.order_id || !data?.key_id) return { status: "unavailable" };

    return {
      status: "order_created",
      orderId: data.order_id,
      amount: data.amount,
      currency: data.currency ?? "INR",
      keyId: data.key_id,
    };
  } catch {
    return { status: "unavailable" };
  }
}

