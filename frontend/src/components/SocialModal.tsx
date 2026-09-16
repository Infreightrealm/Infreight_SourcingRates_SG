"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import {
  X,
  Send,
  MessageSquare,
  Camera,
  Loader2,
  ShieldCheck,
  Sparkles,
  Clock,
  Lock,
  User,
  ArrowLeft,
  ChevronRight,
  TrendingUp,
} from "lucide-react";
import {
  OrbitCardStack,
  type OrbitStackItem,
} from "@/components/ui/orbit-card-stack";
import {
  getColleagues,
  getConversation,
  sendDirectMessage,
  uploadUserAvatar,
  type Colleague,
  type DirectMessageItem,
} from "@/lib/api";
import { toast } from "sonner";

interface SocialModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUserRole?: string | null;
  onAvatarUpdated?: () => void;
}

// Helper to downscale uploaded avatar to compact base64 data URI (~20-40KB)
function resizeImageToDataUrl(file: File, maxDim: number = 280): Promise<string> {
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
        resolve(canvas.toDataURL("image/jpeg", 0.88));
      };
      img.onerror = reject;
      img.src = e.target?.result as string;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

const ACCENT_COLORS = ["#38bdf8", "#f43f5e", "#10b981", "#8b5cf6", "#f59e0b", "#06b6d4", "#ec4899"];

export default function SocialModal({
  isOpen,
  onClose,
  currentUserRole,
  onAvatarUpdated,
}: SocialModalProps) {
  const [colleagues, setColleagues] = useState<Colleague[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedColleague, setSelectedColleague] = useState<Colleague | null>(null);

  // Direct Messaging State
  const [messages, setMessages] = useState<DirectMessageItem[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [inputText, setInputText] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Avatar Upload State (Admin only)
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [targetColleagueForUpload, setTargetColleagueForUpload] = useState<Colleague | null>(null);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  const isAdmin = currentUserRole === "admin";

  // Load colleagues when modal opens
  const fetchColleagues = async () => {
    setLoading(true);
    try {
      const list = await getColleagues();
      setColleagues(list);
    } catch (err: any) {
      toast.error(err.message || "Failed to load colleagues list.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchColleagues();
    } else {
      setSelectedColleague(null);
      setMessages([]);
    }
  }, [isOpen]);

  // Load conversation when a colleague is selected
  const fetchMessages = async (colleagueId: string) => {
    try {
      const history = await getConversation(colleagueId);
      setMessages(history);
      // Auto-update unread count in local list
      setColleagues((prev) =>
        prev.map((c) => (c.id === colleagueId ? { ...c, unread_count: 0 } : c))
      );
    } catch (err: any) {
      toast.error(err.message || "Failed to load chat history.");
    }
  };

  useEffect(() => {
    if (!selectedColleague) return;

    setLoadingMessages(true);
    fetchMessages(selectedColleague.id).finally(() => setLoadingMessages(false));

    // Poll for new messages every 3.5 seconds while chat drawer is open
    const interval = setInterval(() => {
      fetchMessages(selectedColleague.id);
    }, 3500);

    return () => clearInterval(interval);
  }, [selectedColleague]);

  // Scroll to bottom when messages update
  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Send message
  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!selectedColleague || !inputText.trim() || sending) return;

    const content = inputText.trim();
    setInputText("");
    setSending(true);

    try {
      const newMsg = await sendDirectMessage(selectedColleague.id, content);
      setMessages((prev) => [...prev, newMsg]);
    } catch (err: any) {
      toast.error(err.message || "Failed to send message.");
      setInputText(content); // restore on error
    } finally {
      setSending(false);
    }
  };

  // Trigger avatar file chooser
  const handleUploadAvatarClick = (item: OrbitStackItem) => {
    const target = colleagues.find((c) => c.id === item.id);
    if (!target) return;
    setTargetColleagueForUpload(target);
    fileInputRef.current?.click();
  };

  // Handle file selected
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

      // Update state locally
      setColleagues((prev) =>
        prev.map((c) =>
          c.id === targetColleagueForUpload.id ? { ...c, avatar_url: dataUrl } : c
        )
      );

      if (selectedColleague?.id === targetColleagueForUpload.id) {
        setSelectedColleague((prev) => (prev ? { ...prev, avatar_url: dataUrl } : null));
      }

      toast.success(`Profile photo updated for ${targetColleagueForUpload.display_name}!`, { id: toastId });
      onAvatarUpdated?.();
    } catch (err: any) {
      toast.error(err.message || "Failed to upload avatar.", { id: toastId });
    } finally {
      setUploadingAvatar(false);
      setTargetColleagueForUpload(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // Transform colleagues to OrbitStackItems
  const stackItems: OrbitStackItem[] = useMemo(() => {
    return colleagues.map((c, i) => {
      const name = c.display_name || c.name || c.username;
      const initials = name
        .split(" ")
        .map((p) => p[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();

      return {
        id: c.id,
        name: name,
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
  }, [colleagues]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-xl p-4 sm:p-6 overflow-hidden">
      {/* Hidden File Input for Avatar Upload */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/png, image/jpeg, image/webp"
        className="hidden"
      />

      <div className="relative flex flex-col h-[90vh] max-h-[820px] w-full max-w-6xl rounded-3xl border border-white/15 bg-slate-900/95 text-slate-100 shadow-2xl overflow-hidden backdrop-blur-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-6 sm:px-8 py-4 shrink-0 bg-slate-950/40">
          <div className="flex items-center gap-3.5">
            <div className="flex size-10 items-center justify-center rounded-2xl border border-sky-400/30 bg-sky-500/10 text-sky-400 shadow-sm">
              <Sparkles className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg sm:text-xl font-bold tracking-tight text-white">
                  Team Social &amp; Private Texting
                </h2>
                <span className="rounded-full bg-sky-500/20 border border-sky-400/30 px-2.5 py-0.5 text-[10px] font-bold text-sky-300 uppercase tracking-wider">
                  Orbit Deck
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Hover to fan out the card deck · View colleague rate stats · Click any colleague to text privately
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-full p-2 text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
            title="Close"
          >
            <X className="size-5" />
          </button>
        </div>

        {/* Main Content Stage */}
        <div className="relative flex-1 overflow-hidden flex">
          {/* Orbit Card Stack View (Fills modal) */}
          <div
            className={`flex-1 flex flex-col justify-center items-center transition-all duration-500 overflow-hidden ${
              selectedColleague ? "lg:mr-[380px] opacity-40 lg:opacity-100" : ""
            }`}
          >
            {loading ? (
              <div className="flex flex-col items-center gap-3 text-slate-400">
                <Loader2 className="size-8 animate-spin text-sky-400" />
                <span className="text-xs font-medium">Gathering team cards...</span>
              </div>
            ) : (
              <div className="w-full flex-1 flex flex-col justify-center items-center">
                <OrbitCardStack
                  items={stackItems}
                  isAdmin={isAdmin}
                  onSelectMember={(item) => {
                    const target = colleagues.find((c) => c.id === item.id);
                    if (target) setSelectedColleague(target);
                  }}
                  onUploadAvatar={handleUploadAvatarClick}
                />
              </div>
            )}
          </div>

          {/* Private 1-on-1 Chat Drawer (Slides in on right when a colleague is selected) */}
          {selectedColleague && (
            <div className="absolute right-0 top-0 bottom-0 w-full sm:w-[400px] lg:w-[420px] bg-slate-950/95 border-l border-white/15 shadow-2xl flex flex-col z-30 backdrop-blur-2xl transition-all duration-300">
              {/* Chat Drawer Header */}
              <div className="flex items-center justify-between border-b border-white/10 px-5 py-4 bg-slate-900/60">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setSelectedColleague(null)}
                    className="p-1 rounded-lg text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                    title="Back to Orbit Stack"
                  >
                    <ArrowLeft className="size-4" />
                  </button>

                  {/* Colleague Avatar */}
                  <div className="relative size-10 shrink-0 rounded-full border border-white/20 bg-slate-800 overflow-hidden shadow-sm">
                    {selectedColleague.avatar_url ? (
                      <img
                        src={selectedColleague.avatar_url}
                        alt={selectedColleague.display_name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center text-xs font-bold text-sky-300 bg-sky-950/60">
                        {selectedColleague.display_name?.slice(0, 2).toUpperCase()}
                      </div>
                    )}
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                      <span>{selectedColleague.display_name || selectedColleague.name}</span>
                      <span className="text-[10px] font-mono text-slate-400">
                        @{selectedColleague.username}
                      </span>
                    </h3>
                    <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
                      <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span>Private 1-on-1 Texting</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedColleague(null)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                  title="Close conversation"
                >
                  <X className="size-4" />
                </button>
              </div>

              {/* Colleague Quick Stats Bar */}
              <div className="flex items-center justify-between px-5 py-2.5 bg-sky-950/30 border-b border-sky-500/10 text-xs">
                <span className="text-slate-400">Rate Sourcing Velocity:</span>
                <span className="font-mono font-bold text-sky-300">
                  {selectedColleague.stats?.total_searches ?? 0} Quotes Sourced
                </span>
              </div>

              {/* Chat Message Stream */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {loadingMessages ? (
                  <div className="flex h-full items-center justify-center">
                    <Loader2 className="size-6 animate-spin text-sky-400" />
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center p-6 text-slate-400 space-y-2">
                    <div className="size-12 rounded-full bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                      <Lock className="size-5" />
                    </div>
                    <p className="text-xs font-semibold text-white">End-to-End Private Channel</p>
                    <p className="text-[11px] text-slate-400 max-w-xs">
                      Messages between you and @{selectedColleague.username} are private and directly delivered.
                    </p>
                  </div>
                ) : (
                  messages.map((msg) => {
                    const isMe = msg.is_from_me;
                    return (
                      <div
                        key={msg.id}
                        className={`flex flex-col ${isMe ? "items-end" : "items-start"}`}
                      >
                        <div
                          className={`max-w-[82%] rounded-2xl px-4 py-2.5 text-sm shadow-md ${
                            isMe
                              ? "bg-sky-500 text-white rounded-br-xs font-medium"
                              : "bg-slate-800/90 text-slate-100 rounded-bl-xs border border-white/10"
                          }`}
                        >
                          <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                        </div>
                        <span className="mt-1 text-[10px] text-slate-500 font-mono px-1">
                          {msg.created_at
                            ? new Date(msg.created_at).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            : ""}
                        </span>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input */}
              <form onSubmit={handleSend} className="p-3 border-t border-white/10 bg-slate-900/80">
                <div className="flex items-center gap-2 rounded-2xl border border-white/15 bg-slate-950/80 px-3 py-1.5 shadow-inner focus-within:border-sky-400">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={`Message @${selectedColleague.username}...`}
                    className="flex-1 bg-transparent py-1.5 text-sm text-white placeholder:text-slate-500 focus:outline-none"
                    disabled={sending}
                  />
                  <button
                    type="submit"
                    disabled={!inputText.trim() || sending}
                    className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-sky-500 text-white hover:bg-sky-400 disabled:opacity-40 transition-all cursor-pointer"
                  >
                    {sending ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Send className="size-4" />
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
