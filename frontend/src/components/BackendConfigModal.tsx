"use client";
import { useState } from "react";
import { getPrimaryApiUrl, setCustomPrimaryApiUrl, forceRestorePrimary, getApiUrl } from "@/lib/api";
import { Overlay, Panel } from "@/components/ui/surfaces";
import { Input } from "@/components/ui/input";
import { Plug, X } from "lucide-react";
import { toast } from "sonner";

interface BackendConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUrlChanged: (newUrl: string) => void;
}

export default function BackendConfigModal({ isOpen, onClose, onUrlChanged }: BackendConfigModalProps) {
  const [urlInput, setUrlInput] = useState(() => getPrimaryApiUrl());
  const [isTesting, setIsTesting] = useState(false);

  if (!isOpen) return null;

  const handleSaveAndTest = async () => {
    setIsTesting(true);
    const cleaned = urlInput.trim();
    setCustomPrimaryApiUrl(cleaned);
    
    toast.info("Testing connection to " + (cleaned || "Primary Backend") + "...");
    const res = await forceRestorePrimary();
    setIsTesting(false);
    
    if (res.success) {
      toast.success(`Connected to Primary Backend (${res.url})!`);
      onUrlChanged(res.url);
      onClose();
    } else {
      toast.error("Could not connect to Primary Backend", {
        description: res.error,
        duration: 8000,
      });
    }
  };

  const handleReset = () => {
    setCustomPrimaryApiUrl("");
    const defaultUrl = getPrimaryApiUrl();
    setUrlInput(defaultUrl);
    toast.info("Reset primary URL to default.");
  };

  return (
    <Overlay className="z-50">
      <Panel className="max-w-md space-y-5 p-6">
        <div className="flex items-center justify-between border-b border-line pb-3">
          <div className="flex items-center gap-2.5">
            <span className="inline-flex size-8 items-center justify-center rounded-lg border border-border bg-muted text-primary">
              <Plug className="size-4" />
            </span>
            <h3 className="text-base font-semibold tracking-tight">Backend Server Settings</h3>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="flex size-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </div>

        <div className="space-y-4 text-sm">
          <div>
            <label htmlFor="backend-url" className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Primary Backend URL (Local Machine / ngrok Tunnel)
            </label>
            <Input
              id="backend-url"
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="e.g. https://your-tunnel.ngrok-free.app or http://localhost:8000"
              className="font-mono text-xs"
            />
            <p className="mt-1.5 text-[11px] text-muted-foreground">
              If your ngrok tunnel URL changes when you restart ngrok on your computer, paste your new ngrok URL here!
            </p>
          </div>

          <div className="space-y-1 rounded-xl border border-border bg-muted/50 p-3 text-xs">
            <div className="flex justify-between gap-3 text-muted-foreground">
              <span>Active Backend:</span>
              <span className="max-w-[220px] truncate font-mono font-medium text-success-foreground">{getApiUrl()}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <button
            onClick={handleReset}
            className="text-xs text-muted-foreground underline underline-offset-2 transition-colors hover:text-foreground"
          >
            Reset Default
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="btn-interactive rounded-lg border border-border bg-secondary px-4 py-2 text-xs font-medium text-secondary-foreground hover:bg-accent"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveAndTest}
              disabled={isTesting}
              className="btn-interactive rounded-lg bg-primary px-4 py-2 text-xs font-medium text-primary-foreground shadow-brand hover:bg-primary/90 disabled:opacity-50"
            >
              {isTesting ? "Testing..." : "Save & Connect"}
            </button>
          </div>
        </div>
      </Panel>
    </Overlay>
  );
}
