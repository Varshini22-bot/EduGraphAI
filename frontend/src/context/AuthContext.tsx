"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  ReactNode,
} from "react";
import { User } from "@/lib/types";
import {
  getCurrentUser,
  hasToken,
  clearToken,
} from "@/lib/auth/authClient";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Monotonic guard against out-of-order async auth results. Every auth
  // operation (refreshUser / logout) claims the next id; an in-flight
  // getCurrentUser() only commits its result if it still holds the latest
  // id. This is what stops a slow request for a user who has since logged
  // out — or been replaced by a different login — from overwriting the
  // current auth state (e.g. User A's stale /auth/me landing after User B
  // has logged in). Persists across route navigation because AuthProvider
  // lives in the root layout.
  const authRequestRef = useRef(0);

  const refreshUser = useCallback(async () => {
    const requestId = ++authRequestRef.current;

    if (!hasToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    const current = await getCurrentUser();

    // A newer refreshUser()/logout() started while we were awaiting — the
    // result we just fetched is stale, so drop it instead of clobbering the
    // newer state (and leave loading to be resolved by that newer op).
    if (authRequestRef.current !== requestId) return;

    setUser(current);
    setLoading(false);
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const logout = useCallback(() => {
    // Invalidate any in-flight refreshUser() so its result can't revive this
    // session after sign-out.
    authRequestRef.current++;
    clearToken();
    setUser(null);
    setLoading(false);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: !!user, refreshUser, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
