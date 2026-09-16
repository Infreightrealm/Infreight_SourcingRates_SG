"use client";

import { useState } from "react";
import { 
  User, 
  ArrowRight, 
  Loader2, 
  Lock, 
  UserPlus, 
  KeyRound, 
  AlertCircle, 
  CheckCircle2, 
  ShieldCheck 
} from "lucide-react";
import { loginAuth, signupAuth, setupPasswordAuth } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Overlay, Panel } from "@/components/ui/surfaces";
import { toast } from "sonner";

interface LoginModalProps {
  onLogin: (name: string, role?: string) => void;
}

export default function LoginModal({ onLogin }: LoginModalProps) {
  const [activeTab, setActiveTab] = useState<"login" | "signup" | "setup">("login");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Login form
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Signup form
  const [signupName, setSignupName] = useState("");
  const [signupUsername, setSignupUsername] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirm, setSignupConfirm] = useState("");

  // Setup password form
  const [setupUsername, setSetupUsername] = useState("");
  const [setupPasswordInput, setSetupPasswordInput] = useState("");
  const [setupConfirmInput, setSetupConfirmInput] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setLoading(true);

    try {
      const res = await loginAuth(loginUsername.trim(), loginPassword);
      onLogin(res.user.display_name || res.user.name || res.user.username, res.user.role);
    } catch (err: any) {
      if (err.code === "NEEDS_PASSWORD") {
        setSetupUsername(err.username || loginUsername.trim());
        setActiveTab("setup");
        setSuccessMessage("Security upgrade: Please set a new password to continue.");
        toast.info("Existing accounts must set a new password.");
      } else {
        setErrorMessage(err.message || "Incorrect username or password.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (signupPassword !== signupConfirm) {
      setErrorMessage("Passwords do not match.");
      return;
    }
    if (signupPassword.length < 8) {
      setErrorMessage("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      const res = await signupAuth(signupName.trim(), signupUsername.trim(), signupPassword);
      if (res.user.status === "active") {
        onLogin(res.user.display_name || res.user.name || res.user.username, res.user.role);
      } else {
        setSuccessMessage("Access request submitted! An administrator will review your account.");
        setActiveTab("login");
        setLoginUsername(res.user.username);
        toast.info("Request sent! You can sign in once an admin approves your request.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to submit request.");
    } finally {
      setLoading(false);
    }
  };

  const handleSetupPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (setupPasswordInput !== setupConfirmInput) {
      setErrorMessage("Passwords do not match.");
      return;
    }
    if (setupPasswordInput.length < 8) {
      setErrorMessage("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      const res = await setupPasswordAuth(setupUsername.trim(), setupPasswordInput, setupConfirmInput);
      toast.success("Password configured successfully!");
      onLogin(res.user.display_name || res.user.name || res.user.username, res.user.role);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to set password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Overlay>
      <Panel className="max-w-md p-6 sm:p-8">
        <div className="mb-4 flex justify-center">
          <div className="bg-gradient-brand animate-float-gentle flex size-14 items-center justify-center rounded-2xl text-white shadow-brand">
            <ShieldCheck className="size-7" />
          </div>
        </div>

        <div className="mb-6 text-center">
          <h2 className="mb-1 text-2xl font-semibold tracking-tight text-foreground">
            Infreight <span className="text-gradient-brand">Sourcing</span>
          </h2>
          <p className="text-xs text-muted-foreground">
            Internal Freight Intelligence & Ocean Rate Comparison
          </p>
        </div>

        {/* Tab switch */}
        <div className="grid grid-cols-2 gap-1 p-1 bg-muted/60 rounded-xl mb-5">
          <button
            type="button"
            onClick={() => {
              setActiveTab("login");
              setErrorMessage("");
            }}
            className={`py-1.5 px-3 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === "login"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Lock className="size-3.5" />
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab("signup");
              setErrorMessage("");
            }}
            className={`py-1.5 px-3 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === "signup"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <UserPlus className="size-3.5" />
            Request Access
          </button>
        </div>

        {/* Banners */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-start gap-2 animate-fade-in-up">
            <AlertCircle className="size-4 shrink-0 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs flex items-start gap-2 animate-fade-in-up">
            <CheckCircle2 className="size-4 shrink-0 mt-0.5" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* TAB 1: SIGN IN */}
        {activeTab === "login" && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Username or Name</label>
              <div className="relative">
                <Input
                  type="text"
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                  placeholder="e.g. brian"
                  autoFocus
                  required
                  className="pl-9 text-sm"
                />
                <User className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-foreground">Password</label>
                <button
                  type="button"
                  onClick={() => {
                    setSetupUsername(loginUsername);
                    setActiveTab("setup");
                  }}
                  className="text-[11px] text-primary hover:underline"
                >
                  Legacy user? Set password
                </button>
              </div>
              <div className="relative">
                <Input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="pl-9 text-sm"
                />
                <Lock className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <button
              type="submit"
              disabled={!loginUsername.trim() || !loginPassword || loading}
              className="bg-gradient-brand btn-interactive shine-on-hover flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-medium text-white shadow-brand transition-all disabled:cursor-not-allowed disabled:opacity-50 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="size-4" />
                </>
              )}
            </button>
          </form>
        )}

        {/* TAB 2: REQUEST ACCESS */}
        {activeTab === "signup" && (
          <form onSubmit={handleSignup} className="space-y-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Your Full Name</label>
              <Input
                type="text"
                value={signupName}
                onChange={(e) => setSignupName(e.target.value)}
                placeholder="e.g. Brian Lee"
                required
                className="text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Username</label>
              <Input
                type="text"
                value={signupUsername}
                onChange={(e) => setSignupUsername(e.target.value)}
                placeholder="e.g. brian.lee"
                required
                pattern="[a-zA-Z0-9._-]{3,40}"
                className="text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Password (min 8 chars)</label>
              <Input
                type="password"
                value={signupPassword}
                onChange={(e) => setSignupPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Confirm Password</label>
              <Input
                type="password"
                value={signupConfirm}
                onChange={(e) => setSignupConfirm(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={!signupName.trim() || !signupUsername.trim() || !signupPassword || loading}
              className="bg-gradient-brand btn-interactive shine-on-hover flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-medium text-white shadow-brand transition-all disabled:cursor-not-allowed disabled:opacity-50 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Submitting…
                </>
              ) : (
                <>
                  Send Request
                  <ArrowRight className="size-4" />
                </>
              )}
            </button>
          </form>
        )}

        {/* TAB 3 / MODE: SETUP PASSWORD */}
        {activeTab === "setup" && (
          <form onSubmit={handleSetupPassword} className="space-y-3">
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300">
              <p className="font-semibold flex items-center gap-1 mb-1">
                <KeyRound className="size-3.5 text-amber-500" />
                Security Upgrade Required
              </p>
              Set a new password for your account to activate your session.
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Account Username or Name</label>
              <Input
                type="text"
                value={setupUsername}
                onChange={(e) => setSetupUsername(e.target.value)}
                placeholder="e.g. brian"
                required
                className="text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">New Password (min 8 chars)</label>
              <Input
                type="password"
                value={setupPasswordInput}
                onChange={(e) => setSetupPasswordInput(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Confirm New Password</label>
              <Input
                type="password"
                value={setupConfirmInput}
                onChange={(e) => setSetupConfirmInput(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={!setupUsername.trim() || !setupPasswordInput || loading}
              className="bg-gradient-brand btn-interactive shine-on-hover flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-medium text-white shadow-brand transition-all disabled:cursor-not-allowed disabled:opacity-50 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Updating…
                </>
              ) : (
                <>
                  Activate & Sign In
                  <ArrowRight className="size-4" />
                </>
              )}
            </button>

            <div className="text-center pt-1">
              <button
                type="button"
                onClick={() => {
                  setActiveTab("login");
                  setErrorMessage("");
                }}
                className="text-xs text-muted-foreground hover:text-foreground underline"
              >
                Back to Sign In
              </button>
            </div>
          </form>
        )}
      </Panel>
    </Overlay>
  );
}
