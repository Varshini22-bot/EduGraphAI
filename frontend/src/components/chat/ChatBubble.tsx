import { ReactNode } from "react";

interface ChatBubbleProps {
  role: "user" | "assistant";
  children: ReactNode;
}

export default function ChatBubble({ role, children }: ChatBubbleProps) {
  if (role === "user") {
    return (
      <div className="flex justify-end animate-fadein">
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm border border-violet/30 bg-violet-dim px-4 py-2.5 text-sm text-ink-primary">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-fadein">
      <div className="w-full max-w-full">{children}</div>
    </div>
  );
}
