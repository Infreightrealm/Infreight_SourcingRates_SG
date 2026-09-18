"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  X,
  Send,
  Loader2,
  Lock,
  ArrowLeft,
  Search,
  ImagePlus,
  MessagesSquare,
  Camera,
  Layers,
  Hand,
  Trash2,
  AlertTriangle,
  Cloud,
  Laptop,
} from "lucide-react";
import { HalftoneAvatar } from "@/components/ui/halftone-avatar";
import { EmojiPicker } from "@/components/ui/emoji-picker";
import { OrbitCardStack, type OrbitStackItem } from "@/components/ui/orbit-card-stack";
import {
  getColleagues,
  getConversation,
  sendDirectMessage,
  uploadUserAvatar,
  pokeColleague,
  wipeConversation,
  getSocialConnectionInfo,
  type Colleague,
  type DirectMessageItem,
} from "@/lib/api";
import { toast } from "sonner";

interface SocialWidgetProps {
  currentUserRole?: string | null;
  onAvatarUpdated?: () => void;
}

// Downscale an image file/blob to a compact base64 data URI — used for both
// square avatar uploads and pasted chat screenshots.
function resizeImageToDataUrl(file: Blob, maxDim: number = 280, quality: number = 0.88): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        let { width, height } = img;
        if (width > height) {
          if (width > maxDim) {
            height = Math.round((height * maxDim) / width);
            width = maxDim;
          }
        } else {
          if (height > maxDim) {
            width = Math.round((width * maxDim) / height);
            height = maxDim;
          }
        }
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) return reject(new Error("Canvas context failed"));
        ctx.drawImage(img, 0, 0, width, height);
        resolve(canvas.toDataURL("image/jpeg", quality));
      };
      img.onerror = reject;
      img.src = e.target?.result as string;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

const ACCENT_COLORS = ["#38bdf8", "#f43f5e", "#10b981", "#8b5cf6", "#f59e0b", "#06b6d4", "#ec4899"];

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof Error && err.message ? err.message : fallback;
}

function relativeTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const diffMs = Date.now() - then;
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "now";
  if (mins < 60) return `${mins}m`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.round(hours / 24);
  return `${days}d`;
}

export default function SocialWidget({ currentUserRole, onAvatarUpdated }: SocialWidgetProps) {
  const [open, setOpen] = useState(false);
  const [colleagues, setColleagues] = useState<Colleague[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [panelTab, setPanelTab] = useState<"messages" | "team">("messages");
  const [selectedColleague, setSelectedColleague] = useState<Colleague | null>(null);

  // Direct Messaging State
  const [messages, setMessages] = useState<DirectMessageItem[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [inputText, setInputText] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [composerFor, setComposerFor] = useState<string | null>(null);

  // Poke cooldown + two-tap "wipe conversation" arm/confirm
  const [poking, setPoking] = useState(false);
  const [pokeOnCooldown, setPokeOnCooldown] = useState(false);
  const pokeCooldownTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [wipeArmed, setWipeArmed] = useState(false);
  const [wiping, setWiping] = useState(false);
  const wipeDisarmTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Pasted / attached screenshot pending send
  const [pendingImage, setPendingImage] = useState<string | null>(null);
  const [preparingImage, setPreparingImage] = useState(false);
  const imageInputRef = useRef<HTMLInputElement>(null);

  // Avatar Upload State (Admin only)
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [targetColleagueForUpload, setTargetColleagueForUpload] = useState<Colleague | null>(null);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  const isAdmin = currentUserRole === "admin";

  const [connInfo, setConnInfo] = useState(getSocialConnectionInfo());

  const fetchColleagues = async () => {
    try {
      const list = await getColleagues();
      setColleagues(list);
    } catch {
      // Silent — this also polls in the background for the badge count, and a
      // toast every 20s on a flaky connection would be worse than staying quiet.
    } finally {
      setConnInfo(getSocialConnectionInfo());
    }
  };

  // Keep the launcher's unread badge fresh even while the panel is closed.
  useEffect(() => {
    fetchColleagues();
    const interval = setInterval(fetchColleagues, 20000);
    return () => clearInterval(interval);
  }, []);

  // Full refresh (with a spinner) whenever the panel opens; reset back to the
  // list view and clear the filter whenever it closes.
  useEffect(() => {
    if (open) {
      setLoading(true);
      fetchColleagues().finally(() => setLoading(false));
    } else {
      setSelectedColleague(null);
      setQuery("");
      setPanelTab("messages");
    }
  }, [open]);

  const messagesRef = useRef<DirectMessageItem[]>([]);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const fetchMessages = async (colleagueId: string, colleagueName: string) => {
    try {
      const history = await getConversation(colleagueId);
      const priorIds = new Set(messagesRef.current.map((m) => m.id));
      const freshPoke = history.find((m) => m.message_type === "poke" && !m.is_from_me && !priorIds.has(m.id));
      if (freshPoke && messagesRef.current.length > 0) {
        toast(`👋 ${colleagueName} poked you!`);
      }
      setMessages(history);
      setColleagues((prev) =>
        prev.map((c) => (c.id === colleagueId ? { ...c, unread_count: 0 } : c))
      );
    } catch (err) {
      toast.error(errorMessage(err, "Failed to load chat history."));
    }
  };

  // Reset the composer's draft/attachment whenever the focused colleague changes
  // (done during render, not an effect, so it can never flash the old draft first).
  if (composerFor !== (selectedColleague?.id ?? null)) {
    setComposerFor(selectedColleague?.id ?? null);
    setPendingImage(null);
    setInputText("");
    setWipeArmed(false);
    // Cooldown is tracked server-side per-conversation; a stale local timer
    // simply fires later and harmlessly no-ops (state's already false by then).
    setPokeOnCooldown(false);
  }

  useEffect(() => {
    if (!selectedColleague) return;
    const colleagueName = selectedColleague.display_name || selectedColleague.name;
    setLoadingMessages(true);
    fetchMessages(selectedColleague.id, colleagueName).finally(() => setLoadingMessages(false));
    const interval = setInterval(() => fetchMessages(selectedColleague.id, colleagueName), 3500);
    return () => clearInterval(interval);
  }, [selectedColleague]);

  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    return () => {
      if (wipeDisarmTimer.current) clearTimeout(wipeDisarmTimer.current);
      if (pokeCooldownTimer.current) clearTimeout(pokeCooldownTimer.current);
    };
  }, []);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const content = inputText.trim();
    if (!selectedColleague || sending || (!content && !pendingImage)) return;

    setInputText("");
    const attachment = pendingImage ? { url: pendingImage, type: "image" } : null;
    setPendingImage(null);
    setSending(true);

    try {
      const newMsg = await sendDirectMessage(selectedColleague.id, content, attachment);
      setMessages((prev) => [...prev, newMsg]);
    } catch (err) {
      toast.error(errorMessage(err, "Failed to send message."));
      setInputText(content);
      if (attachment) setPendingImage(attachment.url);
    } finally {
      setSending(false);
    }
  };

  const attachImageFile = async (file: File | null | undefined) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Only image files can be attached.");
      return;
    }
    setPreparingImage(true);
    try {
      const dataUrl = await resizeImageToDataUrl(file, 1280, 0.82);
      setPendingImage(dataUrl);
    } catch {
      toast.error("Failed to process the image.");
    } finally {
      setPreparingImage(false);
    }
  };

  const handlePasteImage = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of items) {
      if (item.type.startsWith("image/")) {
        e.preventDefault();
        attachImageFile(item.getAsFile());
        return;
      }
    }
  };

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    attachImageFile(e.target.files?.[0]);
    if (imageInputRef.current) imageInputRef.current.value = "";
  };

  const handleEmojiSelect = (emoji: string) => {
    setInputText((prev) => `${prev}${emoji}`);
  };

  const POKE_COOLDOWN_MS = 10_000;

  const handlePoke = async () => {
    if (!selectedColleague || poking || pokeOnCooldown) return;
    setPoking(true);
    try {
      const newMsg = await pokeColleague(selectedColleague.id);
      setMessages((prev) => [...prev, newMsg]);
      setPokeOnCooldown(true);
      if (pokeCooldownTimer.current) clearTimeout(pokeCooldownTimer.current);
      pokeCooldownTimer.current = setTimeout(() => setPokeOnCooldown(false), POKE_COOLDOWN_MS);
      toast.success(`👋 Poked ${selectedColleague.display_name || selectedColleague.name}`);
    } catch (err) {
      toast.error(errorMessage(err, "Failed to send poke."));
    } finally {
      setPoking(false);
    }
  };

  // Two-tap confirm: first click arms it (auto-disarms after 4s), second
  // click within that window actually deletes — no native confirm() dialog.
  const handleWipeClick = async () => {
    if (!selectedColleague || wiping) return;

    if (!wipeArmed) {
      setWipeArmed(true);
      if (wipeDisarmTimer.current) clearTimeout(wipeDisarmTimer.current);
      wipeDisarmTimer.current = setTimeout(() => setWipeArmed(false), 4000);
      return;
    }

    if (wipeDisarmTimer.current) clearTimeout(wipeDisarmTimer.current);
    setWipeArmed(false);
    setWiping(true);
    try {
      await wipeConversation(selectedColleague.id);
      setMessages([]);
      setColleagues((prev) =>
        prev.map((c) => (c.id === selectedColleague.id ? { ...c, unread_count: 0, last_message: null } : c))
      );
      toast.success("Conversation wiped.");
    } catch (err) {
      toast.error(errorMessage(err, "Failed to wipe conversation."));
    } finally {
      setWiping(false);
    }
  };

  const handleAvatarUploadClick = (e: React.MouseEvent, target: Colleague) => {
    e.stopPropagation();
    setTargetColleagueForUpload(target);
    fileInputRef.current?.click();
  };

  // Same upload flow, triggered from the Team card-fan (OrbitCardStack calls
  // back with its own item shape rather than a Colleague + click event).
  const handleUploadAvatarFromStack = (item: OrbitStackItem) => {
    const target = colleagues.find((c) => c.id === item.id);
    if (!target) return;
    setTargetColleagueForUpload(target);
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !targetColleagueForUpload) return;

    if (!file.type.startsWith("image/")) {
      toast.error("Please choose a valid image file (PNG, JPG, WebP).");
      return;
    }

    setUploadingAvatar(true);
    const toastId = toast.loading(`Uploading profile picture for ${targetColleagueForUpload.display_name}...`);

    try {
      const dataUrl = await resizeImageToDataUrl(file, 280);
      await uploadUserAvatar(targetColleagueForUpload.id, dataUrl);

      setColleagues((prev) =>
        prev.map((c) => (c.id === targetColleagueForUpload.id ? { ...c, avatar_url: dataUrl } : c))
      );
      if (selectedColleague?.id === targetColleagueForUpload.id) {
        setSelectedColleague((prev) => (prev ? { ...prev, avatar_url: dataUrl } : null));
      }

      toast.success(`Profile photo updated for ${targetColleagueForUpload.display_name}!`, { id: toastId });
      onAvatarUpdated?.();
    } catch (err) {
      toast.error(errorMessage(err, "Failed to upload avatar."), { id: toastId });
    } finally {
      setUploadingAvatar(false);
      setTargetColleagueForUpload(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const totalUnread = useMemo(
    () => colleagues.reduce((sum, c) => sum + (c.unread_count || 0), 0),
    [colleagues],
  );

  // Unread conversations first, then most recently texted, then everyone else
  // alphabetically — "you" sinks to the bottom since there's nobody to message there.
  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = colleagues.filter((c) => {
      if (!q) return true;
      const haystack = [c.display_name, c.name, c.username, c.role].filter(Boolean).join(" ").toLowerCase();
      return haystack.includes(q);
    });
    return [...filtered].sort((a, b) => {
      if (a.is_self !== b.is_self) return a.is_self ? 1 : -1;
      if ((b.unread_count || 0) !== (a.unread_count || 0)) return (b.unread_count || 0) - (a.unread_count || 0);
      const aTime = a.last_message?.created_at ? new Date(a.last_message.created_at).getTime() : 0;
      const bTime = b.last_message?.created_at ? new Date(b.last_message.created_at).getTime() : 0;
      if (bTime !== aTime) return bTime - aTime;
      return (a.display_name || a.name || "").localeCompare(b.display_name || b.name || "");
    });
  }, [colleagues, query]);

  // Same filtered roster, reshaped for the Team card-fan view.
  const stackItems: OrbitStackItem[] = useMemo(() => {
    return rows.map((c, i) => {
      const name = c.display_name || c.name || c.username;
      const initials = name
        .split(" ")
        .map((p) => p[0])
        .filter(Boolean)
        .join("")
        .slice(0, 2)
        .toUpperCase();
      return {
        id: c.id,
        name,
        username: c.username,
        role: c.role,
        accent: ACCENT_COLORS[i % ACCENT_COLORS.length],
        initials,
        image: c.avatar_url || undefined,
        isSelf: c.is_self,
        unreadCount: c.unread_count,
        searchStats: c.stats,
      };
    });
  }, [rows]);

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/png, image/jpeg, image/webp"
        className="hidden"
      />

      {/* Anchored panel */}
      {open && (
        <div className="fixed bottom-24 right-4 sm:right-6 z-40 flex h-[min(640px,calc(100vh-8rem))] w-[min(380px,calc(100vw-2rem))] flex-col overflow-hidden rounded-2xl border border-white/15 bg-slate-950/97 text-slate-100 shadow-2xl backdrop-blur-2xl">
          {selectedColleague ? (
            // ---- Chat view ----
            <>
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 bg-slate-900/60 shrink-0">
                <div className="flex min-w-0 items-center gap-2.5">
                  <button
                    onClick={() => setSelectedColleague(null)}
                    className="p-1 rounded-lg text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer shrink-0"
                    title="Back to conversations"
                  >
                    <ArrowLeft className="size-4" />
                  </button>
                  <div className="relative size-9 shrink-0 overflow-hidden rounded-full border border-white/20 bg-[#f3f0e7] shadow-sm">
                    <HalftoneAvatar
                      seed={selectedColleague.username || selectedColleague.id}
                      image={selectedColleague.avatar_url || undefined}
                      alt={selectedColleague.display_name}
                      className="h-full w-full"
                    />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-sm font-bold text-white truncate">
                      {selectedColleague.display_name || selectedColleague.name}
                      <span className="ml-1.5 text-[10px] font-mono font-normal text-slate-400">
                        @{selectedColleague.username}
                      </span>
                    </h3>
                    <div className="flex items-center gap-1.5 text-[10.5px] text-emerald-400 font-medium">
                      <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span>Private 1-on-1</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-0.5 shrink-0">
                  <button
                    onClick={handlePoke}
                    disabled={poking || pokeOnCooldown}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-amber-300 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:text-slate-400"
                    title={`Poke ${selectedColleague.display_name || selectedColleague.name}`}
                  >
                    <Hand className="size-4" />
                  </button>
                  <button
                    onClick={handleWipeClick}
                    disabled={wiping}
                    className={`rounded-lg p-1.5 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${
                      wipeArmed
                        ? "bg-rose-500/20 text-rose-400 hover:bg-rose-500/30"
                        : "text-slate-400 hover:bg-white/10 hover:text-rose-400"
                    }`}
                    title={wipeArmed ? "Click again to permanently delete this conversation" : "Wipe conversation"}
                  >
                    {wipeArmed ? <AlertTriangle className="size-4" /> : <Trash2 className="size-4" />}
                  </button>
                  <button
                    onClick={() => setOpen(false)}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                    title="Close"
                  >
                    <X className="size-4" />
                  </button>
                </div>
              </div>

              {wipeArmed && (
                <div className="flex items-center gap-2 px-4 py-2 bg-rose-500/10 border-b border-rose-500/20 text-[11px] text-rose-300 shrink-0">
                  <AlertTriangle className="size-3.5 shrink-0" />
                  <span className="flex-1">This deletes the whole conversation for both of you. Click the trash icon again to confirm.</span>
                </div>
              )}

              <div className="flex items-center justify-between px-4 py-2 bg-sky-950/30 border-b border-sky-500/10 text-[11px] shrink-0">
                <span className="text-slate-400">Rate Sourcing Velocity:</span>
                <span className="font-mono font-bold text-sky-300">
                  {selectedColleague.stats?.total_searches ?? 0} Quotes Sourced
                </span>
              </div>

              <div className="flex-1 overflow-y-auto p-3.5 space-y-3">
                {loadingMessages ? (
                  <div className="flex h-full items-center justify-center">
                    <Loader2 className="size-6 animate-spin text-sky-400" />
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center p-4 text-slate-400 space-y-2">
                    <div className="size-11 rounded-full bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                      <Lock className="size-5" />
                    </div>
                    <p className="text-xs font-semibold text-white">End-to-End Private Channel</p>
                    <p className="text-[11px] text-slate-400 max-w-[220px]">
                      Messages between you and @{selectedColleague.username} are private and directly delivered.
                    </p>
                  </div>
                ) : (
                  messages.map((msg) => {
                    const isMe = msg.is_from_me;

                    if (msg.message_type === "poke") {
                      return (
                        <div key={msg.id} className="flex flex-col items-center py-1">
                          <div className="flex items-center gap-1.5 rounded-full border border-amber-400/25 bg-amber-500/10 px-3 py-1 text-[11.5px] font-medium text-amber-300">
                            <Hand className="size-3.5" />
                            <span>
                              {isMe
                                ? `You poked ${selectedColleague.display_name || selectedColleague.name}`
                                : `${selectedColleague.display_name || selectedColleague.name} poked you`}
                            </span>
                          </div>
                          <span className="mt-1 text-[10px] text-slate-500 font-mono">
                            {msg.created_at
                              ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                              : ""}
                          </span>
                        </div>
                      );
                    }

                    return (
                      <div key={msg.id} className={`flex flex-col ${isMe ? "items-end" : "items-start"}`}>
                        <div
                          className={`max-w-[85%] overflow-hidden rounded-2xl text-[13.5px] shadow-md ${
                            isMe
                              ? "bg-sky-500 text-white rounded-br-xs font-medium"
                              : "bg-slate-800/90 text-slate-100 rounded-bl-xs border border-white/10"
                          } ${msg.attachment_url ? "p-1.5" : "px-3.5 py-2"}`}
                        >
                          {msg.attachment_url && (
                            <a href={msg.attachment_url} target="_blank" rel="noreferrer">
                              <img
                                src={msg.attachment_url}
                                alt="Shared screenshot"
                                className={`block max-h-60 w-full rounded-xl object-cover ${msg.content ? "mb-1.5" : ""}`}
                              />
                            </a>
                          )}
                          {msg.content && (
                            <p className={`whitespace-pre-wrap break-words ${msg.attachment_url ? "px-2 pb-1" : ""}`}>
                              {msg.content}
                            </p>
                          )}
                        </div>
                        <span className="mt-1 text-[10px] text-slate-500 font-mono px-1">
                          {msg.created_at
                            ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                            : ""}
                        </span>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={handleSend} className="p-2.5 border-t border-white/10 bg-slate-900/80 shrink-0">
                <input
                  type="file"
                  ref={imageInputRef}
                  onChange={handleImageFileChange}
                  accept="image/png, image/jpeg, image/webp, image/gif"
                  className="hidden"
                />

                {(pendingImage || preparingImage) && (
                  <div className="mb-2 flex items-center gap-2 rounded-xl border border-white/10 bg-slate-950/70 p-1.5">
                    {preparingImage ? (
                      <div className="flex size-12 shrink-0 items-center justify-center rounded-lg bg-white/5">
                        <Loader2 className="size-4 animate-spin text-sky-400" />
                      </div>
                    ) : (
                      <img src={pendingImage!} alt="Pending attachment" className="size-12 shrink-0 rounded-lg object-cover" />
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="text-[11px] font-semibold text-white">
                        {preparingImage ? "Processing image…" : "Image ready to send"}
                      </p>
                      <p className="text-[10px] text-slate-500">
                        {preparingImage ? "Paste, drop or pick a screenshot" : "Add a caption or hit send"}
                      </p>
                    </div>
                    {!preparingImage && (
                      <button
                        type="button"
                        onClick={() => setPendingImage(null)}
                        className="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                        title="Remove attachment"
                      >
                        <X className="size-3.5" />
                      </button>
                    )}
                  </div>
                )}

                <div className="flex items-center gap-1 rounded-2xl border border-white/15 bg-slate-950/80 pl-1.5 pr-2.5 py-1.5 shadow-inner focus-within:border-sky-400">
                  <button
                    type="button"
                    onClick={() => imageInputRef.current?.click()}
                    className="flex size-7.5 shrink-0 items-center justify-center rounded-xl text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                    title="Attach an image"
                    aria-label="Attach an image"
                  >
                    <ImagePlus className="size-4" />
                  </button>
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onPaste={handlePasteImage}
                    placeholder={pendingImage ? "Add a caption..." : "Message... (paste a screenshot)"}
                    className="flex-1 min-w-0 bg-transparent py-1.5 text-[13px] text-white placeholder:text-slate-500 focus:outline-none"
                    disabled={sending}
                  />
                  <EmojiPicker onSelect={handleEmojiSelect} />
                  <button
                    type="submit"
                    disabled={(!inputText.trim() && !pendingImage) || sending || preparingImage}
                    className="flex size-7.5 shrink-0 items-center justify-center rounded-xl bg-sky-500 text-white hover:bg-sky-400 disabled:opacity-40 transition-all cursor-pointer"
                  >
                    {sending ? <Loader2 className="size-3.5 animate-spin" /> : <Send className="size-3.5" />}
                  </button>
                </div>
              </form>
            </>
          ) : (
            // ---- Conversation list view ----
            <>
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3.5 bg-slate-900/60 shrink-0">
                <div>
                  <h2 className="text-sm font-bold text-white">Team Social</h2>
                  <div className="flex items-center gap-1.5">
                    <p className="text-[11px] text-slate-400">Private colleague messaging</p>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full border px-1.5 py-px text-[9px] font-semibold uppercase tracking-wide ${
                        connInfo.mode === "cloud"
                          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                          : connInfo.mode === "fallback"
                            ? "border-amber-500/30 bg-amber-500/10 text-amber-400"
                            : "border-white/10 bg-white/5 text-slate-500"
                      }`}
                      title={`Serving Social from: ${connInfo.url || "unknown"}`}
                    >
                      {connInfo.mode === "cloud" ? (
                        <Cloud className="size-2.5" />
                      ) : (
                        <Laptop className="size-2.5" />
                      )}
                      {connInfo.mode === "cloud" ? "Cloud" : connInfo.mode === "fallback" ? "Fallback" : "—"}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                  title="Close"
                >
                  <X className="size-4" />
                </button>
              </div>

              <div className="flex items-center gap-2 border-b border-white/10 bg-slate-950/40 px-3.5 py-2 shrink-0">
                <Search className="size-3.5 shrink-0 text-slate-500" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Find a colleague..."
                  aria-label="Filter colleagues"
                  className="w-full bg-transparent text-[12.5px] text-white placeholder:text-slate-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-1 border-b border-white/10 bg-slate-950/30 p-1.5 shrink-0">
                <button
                  type="button"
                  onClick={() => setPanelTab("messages")}
                  className={`flex items-center justify-center gap-1.5 rounded-lg py-1.5 text-[11.5px] font-semibold transition-colors cursor-pointer ${
                    panelTab === "messages" ? "bg-sky-500/90 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  <MessagesSquare className="size-3.5" />
                  Messages
                </button>
                <button
                  type="button"
                  onClick={() => setPanelTab("team")}
                  className={`flex items-center justify-center gap-1.5 rounded-lg py-1.5 text-[11.5px] font-semibold transition-colors cursor-pointer ${
                    panelTab === "team" ? "bg-sky-500/90 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  <Layers className="size-3.5" />
                  Team
                </button>
              </div>

              {panelTab === "team" ? (
                <div className="flex-1 overflow-y-auto py-2">
                  {loading ? (
                    <div className="flex h-full items-center justify-center">
                      <Loader2 className="size-6 animate-spin text-sky-400" />
                    </div>
                  ) : stackItems.length === 0 ? (
                    <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center text-slate-400">
                      <p className="text-xs font-semibold text-white">No colleague matches “{query}”</p>
                      <button onClick={() => setQuery("")} className="text-xs font-semibold text-sky-400 hover:text-sky-300 cursor-pointer">
                        Clear the filter
                      </button>
                    </div>
                  ) : (
                    <OrbitCardStack
                      items={stackItems}
                      isAdmin={isAdmin}
                      onSelectMember={(item) => {
                        const target = colleagues.find((c) => c.id === item.id);
                        if (target) setSelectedColleague(target);
                      }}
                      onUploadAvatar={handleUploadAvatarFromStack}
                    />
                  )}
                </div>
              ) : (
              <div className="flex-1 overflow-y-auto">
                {loading ? (
                  <div className="flex h-full items-center justify-center">
                    <Loader2 className="size-6 animate-spin text-sky-400" />
                  </div>
                ) : rows.length === 0 ? (
                  <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center text-slate-400">
                    <p className="text-xs font-semibold text-white">No colleague matches “{query}”</p>
                    <button onClick={() => setQuery("")} className="text-xs font-semibold text-sky-400 hover:text-sky-300 cursor-pointer">
                      Clear the filter
                    </button>
                  </div>
                ) : (
                  rows.map((c) => {
                    const name = c.display_name || c.name || c.username;
                    const preview = c.last_message?.content
                      ? `${c.last_message.is_from_me ? "You: " : ""}${c.last_message.content}`
                      : "No messages yet — say hi";
                    const canEditAvatar = isAdmin || c.is_self;

                    return (
                      // A <div role="button"> rather than a real <button> — this row hosts a
                      // second, independently-clickable avatar-upload button, and nesting
                      // <button> inside <button> is invalid HTML.
                      <div
                        key={c.id}
                        role="button"
                        tabIndex={c.is_self ? -1 : 0}
                        onClick={() => !c.is_self && setSelectedColleague(c)}
                        onKeyDown={(e) => {
                          if (!c.is_self && (e.key === "Enter" || e.key === " ")) {
                            e.preventDefault();
                            setSelectedColleague(c);
                          }
                        }}
                        className={`group flex w-full items-center gap-3 border-b border-white/5 px-3.5 py-2.5 text-left transition-colors outline-none focus-visible:bg-white/5 ${
                          c.is_self ? "cursor-default opacity-70" : "cursor-pointer hover:bg-white/5"
                        }`}
                      >
                        <div className="relative shrink-0">
                          <div className="relative size-10 overflow-hidden rounded-full border border-white/15 bg-[#f3f0e7]">
                            <HalftoneAvatar seed={c.username || c.id} image={c.avatar_url || undefined} alt={name} className="h-full w-full" />
                          </div>
                          {(c.unread_count ?? 0) > 0 && (
                            <span className="absolute -top-1 -right-1 flex size-4.5 items-center justify-center rounded-full bg-rose-500 text-[9px] font-extrabold text-white ring-2 ring-slate-950">
                              {c.unread_count}
                            </span>
                          )}
                          {canEditAvatar && (
                            <button
                              type="button"
                              onClick={(e) => handleAvatarUploadClick(e, c)}
                              className="absolute -bottom-1 -right-1 hidden size-5 items-center justify-center rounded-full border border-white/20 bg-slate-800 text-slate-200 hover:bg-sky-500 hover:text-white group-hover:flex"
                              title={c.is_self ? "Update your profile picture" : `Upload profile picture for ${name}`}
                            >
                              <Camera className="size-2.5" />
                            </button>
                          )}
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-2">
                            <p className="truncate text-[13px] font-semibold text-white">
                              {name}
                              {c.is_self && <span className="ml-1.5 text-[10px] font-normal text-amber-400">(you)</span>}
                            </p>
                            {c.last_seen && (
                              <span
                                className="shrink-0 text-[10px] text-slate-500"
                                title={`Last seen ${new Date(c.last_seen).toLocaleString()}`}
                              >
                                {relativeTime(c.last_seen)}
                              </span>
                            )}
                          </div>
                          <p className="truncate text-[11.5px] text-slate-400">{c.is_self ? "This is you" : preview}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Floating launcher */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-40 flex size-14 items-center justify-center rounded-full bg-sky-500 text-white shadow-lg shadow-sky-500/30 transition-transform hover:scale-105 hover:bg-sky-400 cursor-pointer"
        title={open ? "Close Team Social" : "Team Social — colleague messaging"}
      >
        {open ? (
          <X className="size-5" />
        ) : (
          <>
            <MessagesSquare className="size-6" />
            {totalUnread > 0 && (
              <span className="absolute -top-1 -right-1 flex size-5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-extrabold text-white ring-2 ring-slate-950 animate-pulse">
                {totalUnread > 9 ? "9+" : totalUnread}
              </span>
            )}
          </>
        )}
      </button>

      {uploadingAvatar && (
        <div className="fixed bottom-24 right-6 z-50 flex items-center gap-2 rounded-xl border border-white/15 bg-slate-950/95 px-3.5 py-2.5 text-xs font-medium text-white shadow-2xl">
          <Loader2 className="size-4 animate-spin text-sky-400" />
          Uploading profile picture...
        </div>
      )}
    </>
  );
}
