"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { User } from "@/lib/types";

interface AccountMenuProps {
  user: User;
  onSignOut: () => void;
}

export default function AccountMenu({ user, onSignOut }: AccountMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const displayName = user.full_name || user.email;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2.5 rounded-lg p-2 text-left transition-colors hover:bg-hoverbg"
      >
        <div className="flex h-[34px] w-[34px] flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet to-[#5c53c9] text-[13px] font-bold text-white">
          {displayName.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-[13px] font-semibold text-ink-primary">
            {displayName}
          </div>
          <div className="text-[11.5px] text-ink-tertiary">
            {user.is_active ? "Active" : "Inactive"}
          </div>
        </div>
      </button>

      {open && (
        <div className="absolute bottom-full left-0 mb-1 w-full overflow-hidden rounded-lg border border-border-subtle bg-elevated shadow-elevated animate-fadein">
          <Link
            href="/profile"
            onClick={() => setOpen(false)}
            className="block px-3.5 py-2.5 text-[13px] text-ink-secondary hover:bg-hoverbg hover:text-ink-primary"
          >
            Profile
          </Link>
          <Link
            href="/settings"
            onClick={() => setOpen(false)}
            className="block px-3.5 py-2.5 text-[13px] text-ink-secondary hover:bg-hoverbg hover:text-ink-primary"
          >
            Settings
          </Link>
          <button
            onClick={() => {
              setOpen(false);
              onSignOut();
            }}
            className="block w-full px-3.5 py-2.5 text-left text-[13px] text-danger hover:bg-danger-dim"
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
