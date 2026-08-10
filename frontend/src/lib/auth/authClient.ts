import { User } from "../types";
import { ApiError, getBaseUrl } from "../api";

// ---------------------------------------------------------------------------
// LIVE auth client — talks to the verified backend contract:
//   POST /auth/register  (application/json)
//   POST /auth/login     (application/x-www-form-urlencoded, fields
//                          "username"=email, "password"=password)
//   GET  /auth/me         (Authorization: Bearer <token>)
//
// Only the JWT access_token is persisted client-side — never a fabricated
// user object. The user record itself always comes from /auth/me.
// ---------------------------------------------------------------------------

const TOKEN_KEY = "kgla_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function hasToken(): boolean {
  return getToken() !== null;
}

function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body && typeof body.detail === "string") return `: ${body.detail}`;
  } catch {
    // error body wasn't JSON — ignore
  }
  return "";
}

/**
 * POST /auth/login — form-encoded, field name is "username" (OAuth2 spec),
 * not "email". Stores only the access_token on success.
 */
export async function signIn(email: string, password: string): Promise<void> {
  const baseUrl = getBaseUrl();
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  let res: Response;
  try {
    res = await fetch(`${baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
  } catch {
    throw new ApiError(
      `Could not reach the backend at ${baseUrl}.`,
      "network"
    );
  }

  if (!res.ok) {
    const detail = await parseErrorDetail(res);
    throw new ApiError(`Login failed (HTTP ${res.status})${detail}`, "http", res.status);
  }

  let data: { access_token?: string };
  try {
    data = await res.json();
  } catch {
    throw new ApiError("Login response could not be parsed as JSON.", "parse");
  }

  if (!data.access_token) {
    throw new ApiError("Login response did not include an access_token.", "empty");
  }

  setToken(data.access_token);
}

/**
 * POST /auth/register — JSON body. Registration alone does not log the
 * user in (backend returns a UserResponse, not a token), so this signs
 * the new user in immediately afterward to preserve the prior UX where
 * signUp() left the caller authenticated.
 */
export async function signUp(
  fullName: string,
  email: string,
  password: string
): Promise<void> {
  const baseUrl = getBaseUrl();

  let res: Response;
  try {
    res = await fetch(`${baseUrl}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, full_name: fullName, password }),
    });
  } catch {
    throw new ApiError(
      `Could not reach the backend at ${baseUrl}.`,
      "network"
    );
  }

  if (!res.ok) {
    const detail = await parseErrorDetail(res);
    throw new ApiError(`Registration failed (HTTP ${res.status})${detail}`, "http", res.status);
  }

  await signIn(email, password);
}

/**
 * GET /auth/me — Authorization: Bearer <token>. Async (unlike the previous
 * mock implementation). Returns null if there's no token, the token is
 * invalid/expired (401 — token is cleared), or the request otherwise fails.
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = getToken();
  if (!token) return null;

  const baseUrl = getBaseUrl();
  let res: Response;
  try {
    res = await fetch(`${baseUrl}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch {
    return null;
  }

  if (res.status === 401) {
    clearToken();
    return null;
  }

  if (!res.ok) return null;

  try {
    return (await res.json()) as User;
  } catch {
    return null;
  }
}

export function signOut(): void {
  clearToken();
}

// ---------------------------------------------------------------------------
// No backend endpoint exists (verified) for password reset. Left as a
// harmless local no-op so the existing forgot-password page keeps working;
// not presented as backend-confirmed behavior anywhere in the UI copy.
// ---------------------------------------------------------------------------
export async function requestPasswordReset(_email: string): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 500));
}
