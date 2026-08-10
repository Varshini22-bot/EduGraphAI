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
import {
  DEFAULT_SETTINGS,
  loadSettings,
  saveSettings,
  SettingsPreferences,
} from "@/lib/settingsStorage";

interface SettingsContextValue {
  settings: SettingsPreferences;
  updateSetting: <K extends keyof SettingsPreferences>(
    key: K,
    value: SettingsPreferences[K]
  ) => void;
  resolvedTheme: "light" | "dark";
}

const SettingsContext = createContext<SettingsContextValue | undefined>(undefined);

function resolveTheme(
  preference: SettingsPreferences["theme"],
  systemPrefersDark: boolean
): "light" | "dark" {
  if (preference === "system") return systemPrefersDark ? "dark" : "light";
  return preference;
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<SettingsPreferences>(DEFAULT_SETTINGS);
  const [systemPrefersDark, setSystemPrefersDark] = useState(true);
  const hasHydrated = useRef(false);

  // Load saved preferences once on mount (client-only — avoids the
  // hydration mismatch a synchronous localStorage read in initial state
  // would cause).
  useEffect(() => {
    setSettings(loadSettings());
    hasHydrated.current = true;
  }, []);

  // Track the OS/browser preference live, for "system" theme.
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    setSystemPrefersDark(mql.matches);

    function handleChange(event: MediaQueryListEvent) {
      setSystemPrefersDark(event.matches);
    }
    mql.addEventListener("change", handleChange);
    return () => mql.removeEventListener("change", handleChange);
  }, []);

  const resolvedTheme = resolveTheme(settings.theme, systemPrefersDark);

  // Apply theme + compact mode to <html> imperatively. This runs outside
  // React's JSX render of <html> (in layout.tsx), so there is nothing for
  // React to hydrate-mismatch against — it's a plain DOM attribute set
  // after mount, the same pattern next-themes itself uses.
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", resolvedTheme);
  }, [resolvedTheme]);

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-compact",
      settings.compactMode ? "true" : "false"
    );
  }, [settings.compactMode]);

  // Persist on every change, after initial hydration.
  useEffect(() => {
    if (!hasHydrated.current) return;
    saveSettings(settings);
  }, [settings]);

  const updateSetting = useCallback(
    <K extends keyof SettingsPreferences>(key: K, value: SettingsPreferences[K]) => {
      setSettings((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, resolvedTheme }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings(): SettingsContextValue {
  const ctx = useContext(SettingsContext);
  if (!ctx) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return ctx;
}
