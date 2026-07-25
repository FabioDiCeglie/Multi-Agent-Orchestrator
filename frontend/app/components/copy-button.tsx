"use client";

import { useState } from "react";

interface CopyButtonProps {
  text: string;
}

/** Small "copy to clipboard" affordance that briefly confirms success. */
export function CopyButton({ text }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard access can fail (e.g. insecure context) — fail silently.
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 text-xs text-text-muted transition-colors hover:text-text-secondary"
    >
      {copied ? (
        <>
          <span className="text-green-400">✓</span> Copied
        </>
      ) : (
        <>
          <svg
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          Copy
        </>
      )}
    </button>
  );
}
