"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatWidgetProps {
  backendUrl: string;
}

export default function ChatWidget({ backendUrl }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I am your Infreight AI Assistant. Ask me anything about the system status, carrier connectors, or how to handle CAPTCHAs!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: json_body(input, messages),
      });

      if (!response.ok) {
        throw new Error("API network failure");
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I'm having trouble connecting to the backend. Please check if the backend service is running.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to build body payload
  const json_body = (message: string, history: Message[]) => {
    return JSON.stringify({
      message,
      history: history.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });
  };

  return (
    <div className="fixed bottom-6 left-6 z-40 flex flex-col items-start">
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          btn-interactive flex items-center gap-2 rounded-full border border-white/15
          bg-gradient-brand px-4 py-2.5 text-white shadow-brand hover:brightness-110
          ${!isOpen ? 'animate-glow-pulse' : ''}
        `}
        title="Open Infreight Assistant"
        id="chat-floating-btn"
      >
        {isOpen ? (
          <>
            <svg className="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span className="text-[10px] sm:text-xs font-bold tracking-wider uppercase">Close Chat</span>
          </>
        ) : (
          <>
            <div className="relative flex items-center justify-center">
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400" />
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <span className="text-[10px] sm:text-xs font-bold tracking-wider uppercase">Ask AI Assistant</span>
          </>
        )}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div
          className="
            absolute bottom-16 left-0
            w-80 sm:w-96 h-[480px]
            bg-popover/95 backdrop-blur-xl
            border border-border rounded-2xl shadow-card-hover
            flex flex-col overflow-hidden
            animate-scale-in-spring
          "
          style={{ transformOrigin: 'bottom left' }}
        >
          {/* Header */}
          <div className="bg-gradient-brand flex items-center justify-between px-4 py-3 text-white">
            <div className="flex items-center gap-2">
              <div className="size-2 animate-pulse rounded-full bg-emerald-300" />
              <div>
                <h3 className="text-xs font-bold tracking-wide">INFREIGHT ASSISTANT</h3>
                <p className="text-[10px] text-white/70">Powered by Gemini AI</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/80 hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex animate-fade-in-up ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                <div
                  className={`
                    max-w-[85%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-sm
                    ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground rounded-br-none"
                        : "bg-muted text-foreground rounded-bl-none border border-border"
                    }
                  `}
                >
                  <p className="whitespace-pre-line">{msg.content}</p>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-none border border-border bg-muted px-4 py-2.5 text-foreground shadow-panel">
                  <div className="flex items-center gap-1">
                    <span className="animate-wave size-1.5 rounded-full bg-muted-foreground" style={{ animationDelay: "0ms" }} />
                    <span className="animate-wave size-1.5 rounded-full bg-muted-foreground" style={{ animationDelay: "150ms" }} />
                    <span className="animate-wave size-1.5 rounded-full bg-muted-foreground" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Form Input */}
          <form onSubmit={handleSend} className="flex gap-2 border-t border-border bg-muted/40 p-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="
                flex-1 rounded-xl border border-input bg-card px-3.5 py-2 text-xs
                text-foreground shadow-xs outline-none transition-[color,box-shadow,border-color]
                placeholder:text-muted-foreground/70
                focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/22
              "
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="
                btn-interactive flex items-center justify-center rounded-xl bg-primary px-3
                text-xs font-medium text-primary-foreground shadow-panel
                hover:bg-primary/90 disabled:opacity-50
              "
            >
              <svg className="w-4 h-4 transform rotate-90" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
