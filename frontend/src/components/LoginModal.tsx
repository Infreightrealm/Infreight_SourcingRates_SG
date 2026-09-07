import { useState } from "react";
import { User, ArrowRight, Loader2 } from "lucide-react";
import { API_URL } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Overlay, Panel } from "@/components/ui/surfaces";

interface LoginModalProps {
  onLogin: (name: string) => void;
}

export default function LoginModal({ onLogin }: LoginModalProps) {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/users/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: trimmed }),
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to login");
      }
      
      onLogin(data.name);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Overlay>
      <Panel className="max-w-md p-8">
        <div className="mb-6 flex justify-center">
          <div className="bg-gradient-brand animate-float-gentle flex size-16 items-center justify-center rounded-2xl text-white shadow-brand">
            <User className="size-8" />
          </div>
        </div>

        <div className="mb-8 text-center">
          <h2 className="animate-fade-in-up stagger-2 mb-2 text-2xl font-semibold tracking-tight text-foreground">
            Welcome to <span className="text-gradient-brand">Infreight</span>
          </h2>
          <p className="animate-fade-in-up stagger-3 text-sm text-muted-foreground">
            Enter your name to start sourcing rates.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Brian"
            aria-label="Your name"
            autoFocus
            required
            className="py-3 text-center text-lg"
          />

          <button
            type="submit"
            disabled={!name.trim() || loading}
            className="bg-gradient-brand btn-interactive shine-on-hover flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3.5 font-medium text-white shadow-brand transition-all disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="size-5 animate-spin" />
                Signing in…
              </>
            ) : (
              <>
                Start Sourcing
                <ArrowRight className="size-5" />
              </>
            )}
          </button>
        </form>
      </Panel>
    </Overlay>
  );
}
