import type { Config } from "tailwindcss";

// ---------------------------------------------------------------------------
// Colors are now CSS-variable-backed (rgb(var(--x) / <alpha-value>)) instead
// of hardcoded hex. This is what makes real theme switching possible: the
// class names below (bg-elevated, text-ink-primary, etc.) never change in
// any component — only the variable values in globals.css change based on
// [data-theme]. Nothing that already uses these class names needs editing.
// ---------------------------------------------------------------------------

const config: Config = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "rgb(var(--color-base) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        elevated: "rgb(var(--color-elevated) / <alpha-value>)",
        hoverbg: "rgb(var(--color-hoverbg) / <alpha-value>)",
        inputbg: "rgb(var(--color-inputbg) / <alpha-value>)",
        border: {
          subtle: "rgb(var(--color-border-subtle) / <alpha-value>)",
          strong: "rgb(var(--color-border-strong) / <alpha-value>)",
        },
        ink: {
          primary: "rgb(var(--color-ink-primary) / <alpha-value>)",
          secondary: "rgb(var(--color-ink-secondary) / <alpha-value>)",
          tertiary: "rgb(var(--color-ink-tertiary) / <alpha-value>)",
        },
        teal: {
          DEFAULT: "rgb(var(--color-teal) / <alpha-value>)",
          dim: "rgb(var(--color-teal) / 0.14)",
        },
        violet: {
          DEFAULT: "rgb(var(--color-violet) / <alpha-value>)",
          dim: "rgb(var(--color-violet) / 0.16)",
        },
        amber: {
          DEFAULT: "rgb(var(--color-amber) / <alpha-value>)",
          dim: "rgb(var(--color-amber) / 0.14)",
        },
        danger: {
          DEFAULT: "rgb(var(--color-danger) / <alpha-value>)",
          dim: "rgb(var(--color-danger) / 0.14)",
        },
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      boxShadow: {
        elevated: "0 12px 32px rgba(0,0,0,0.45)",
      },
      keyframes: {
        fadein: {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulse2: {
          "0%, 80%, 100%": { opacity: "0.25", transform: "scale(0.85)" },
          "40%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
        toastIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        fadein: "fadein 0.25s ease-out",
        pulse2: "pulse2 1.1s ease-in-out infinite",
        shimmer: "shimmer 1.6s linear infinite",
        toastIn: "toastIn 0.2s ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
