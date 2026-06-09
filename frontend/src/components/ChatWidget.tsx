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
        className="
          w-12 h-12 rounded-full 
          bg-gradient-to-br from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700
          text-white shadow-xl shadow-indigo-500/30 hover:scale-105 active:scale-95
          flex items-center justify-center transition-all duration-200 border border-white/20
        "
        title="Open Infreight Assistant"
        id="chat-floating-btn"
      >
        {isOpen ? (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        )}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div
          className="
            absolute bottom-16 left-0
            w-80 sm:w-96 h-[480px]
            bg-slate-50/95 dark:bg-[#0b0c14]/95 backdrop-blur-xl
            border border-slate-300 dark:border-white/10 rounded-2xl
            shadow-2xl shadow-black/25 dark:shadow-black/50
            flex flex-col overflow-hidden
            animate-in fade-in slide-in-from-bottom-6 duration-200
          "
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-white flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
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
          <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-white/10">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`
                    max-w-[85%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-sm
                    ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-br-none"
                        : "bg-slate-200 dark:bg-white/5 text-slate-800 dark:text-white/95 rounded-bl-none border border-slate-300/30 dark:border-white/5"
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
                <div className="bg-slate-200 dark:bg-white/5 border border-slate-300/30 dark:border-white/5 text-slate-800 dark:text-white/95 rounded-2xl rounded-bl-none px-4 py-2.5 shadow-sm">
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 dark:bg-white/50 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 dark:bg-white/50 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 dark:bg-white/50 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Form Input */}
          <form onSubmit={handleSend} className="p-3 border-t border-slate-300 dark:border-white/10 bg-slate-100 dark:bg-white/[0.01] flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="
                flex-1 px-3.5 py-2 rounded-xl text-xs
                bg-white dark:bg-black/40 border border-slate-300 dark:border-white/10
                text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30
                focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500
                transition-all duration-150
              "
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="
                px-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs
                disabled:opacity-50 disabled:hover:bg-blue-600 transition-all duration-150
                flex items-center justify-center shadow-md shadow-blue-500/10
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
