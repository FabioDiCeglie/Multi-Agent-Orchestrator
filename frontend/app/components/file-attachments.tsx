"use client";

import { useRef } from "react";

interface FileAttachmentsProps {
  files: File[];
  onAdd: (files: File[]) => void;
  onRemove: (index: number) => void;
}

export function FileAttachments({ files, onAdd, onRemove }: FileAttachmentsProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onAdd(Array.from(e.target.files ?? []));
    e.target.value = "";
  };

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="flex items-center gap-1.5 text-xs text-text-secondary transition-colors hover:text-text-primary"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
        </svg>
        Attach files
      </button>
      <input ref={inputRef} type="file" multiple hidden onChange={handleChange} />

      {files.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {files.map((file, i) => (
            <span
              key={`${file.name}-${i}`}
              className="flex items-center gap-1.5 rounded-full border border-border bg-surface-2 pl-2.5 pr-1.5 py-1 text-[11px] text-text-secondary"
            >
              {file.name}
              <button
                type="button"
                onClick={() => onRemove(i)}
                aria-label={`Remove ${file.name}`}
                className="flex size-3.5 items-center justify-center rounded-full text-text-muted transition-colors hover:bg-surface-3 hover:text-text-primary"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
