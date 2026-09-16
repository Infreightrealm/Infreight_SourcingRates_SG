"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { 
  ShieldCheck, 
  ArrowRight, 
  Loader2, 
  Lock, 
  User, 
  UserPlus, 
  KeyRound, 
  CheckCircle2, 
  AlertCircle,
  Ship,
  Sparkles,
  Layers
} from "lucide-react";
import { loginAuth, signupAuth, setupPasswordAuth, getMe } from "@/lib/api";
import { SilkAurora } from "@/components/ui/silk-aurora";
import { DitheredLogo } from "@/components/ui/dithered-logo";
import { toast } from "sonner";

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTarget = searchParams.get("redirect") || "/";

  const [activeTab, setActiveTab] = useState<"login" | "signup" | "setup">("login");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Login form state
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Signup form state
  const [signupName, setSignupName] = useState("");
  const [signupUsername, setSignupUsername] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirm, setSignupConfirm] = useState("");

  // Setup password state (for legacy users)
  const [setupUsername, setSetupUsername] = useState("");
  const [setupPasswordInput, setSetupPasswordInput] = useState("");
  const [setupConfirmInput, setSetupConfirmInput] = useState("");

  // Check if already signed in on mount
  useEffect(() => {
    getMe()
      .then((data) => {
        if (data?.user?.status === "active") {
          router.replace(redirectTarget);
        }
      })
      .catch(() => {
        // Not logged in, stay on login page
      });
  }, [redirectTarget, router]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setLoading(true);

    try {
      const res = await loginAuth(loginUsername.trim(), loginPassword);
      toast.success(`Welcome back, ${res.user.display_name || res.user.name || res.user.username}!`);
      router.push(redirectTarget);
    } catch (err: any) {
      if (err.code === "NEEDS_PASSWORD") {
        setSetupUsername(err.username || loginUsername.trim());
        setActiveTab("setup");
        setErrorMessage("");
        setSuccessMessage("Security upgrade: All existing accounts must set a new password to continue.");
        toast.info("Please set a new password to activate your account.");
      } else {
        setErrorMessage(err.message || "Failed to sign in. Please verify your credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (signupPassword !== signupConfirm) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    if (signupPassword.length < 8) {
      setErrorMessage("Password must be at least 8 characters long.");
      return;
    }

    setLoading(true);
    try {
      const res = await signupAuth(signupName.trim(), signupUsername.trim(), signupPassword);
      if (res.user.status === "active") {
        toast.success("Administrator account created! Logging you in...");
        router.push(redirectTarget);
      } else {
        setSuccessMessage("Access request submitted! An administrator will review and approve your account.");
        setActiveTab("login");
        setLoginUsername(res.user.username);
        setSignupName("");
        setSignupUsername("");
        setSignupPassword("");
        setSignupConfirm("");
        toast.info("Request sent! You can log in as soon as an admin approves your account.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to request account.");
    } finally {
      setLoading(false);
    }
  };

  const handleSetupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (setupPasswordInput !== setupConfirmInput) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    if (setupPasswordInput.length < 8) {
      setErrorMessage("Password must be at least 8 characters long.");
      return;
    }

    setLoading(true);
    try {
      const res = await setupPasswordAuth(setupUsername.trim(), setupPasswordInput, setupConfirmInput);
      toast.success("Password configured successfully! Welcome to Infreight.");
      router.push(redirectTarget);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to configure password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SilkAurora
      fullBleed
      baseColor="#020617"
      midColor="#0c243c"
      sheenColor="#93c5fd"
      accentColor="#0284c7"
      speed={0.85}
      intensity={1.05}
      className="min-h-screen w-full select-none"
    >
      <div className="w-full min-h-screen flex items-center justify-center p-6 sm:p-10 lg:p-14 relative z-10">
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 items-center">
          
          {/* Left Column: Hero & Dithered Interactive Logo */}
          <div className="lg:col-span-7 space-y-8 text-white">
            {/* Logo and Brand Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
              <div className="relative group">
                <DitheredLogo 
                  imageSrc="/infreight-relogo.png" 
                  className="h-24 w-44 sm:h-28 sm:w-52 text-sky-400"
                  dotScale={1.15}
                  scale={0.88}
                  particleColor="#38bdf8"
                  threshold={60}
                  contrast={25}
                  blur={1.8}
                />
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-extrabold tracking-widest text-lg sm:text-xl text-white">
                    INFREIGHT LOGISTICS
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-sky-500/20 text-sky-300 border border-sky-500/30">
                    RATES
                  </span>
                </div>
                <p className="text-xs tracking-wide text-amber-400 font-semibold">
                  Deliver Care, Deliver Excellence
                </p>
                <p className="text-xs text-slate-300/80 font-mono">
                  Multi-Carrier Rate Sourcing & Intelligence Desk
                </p>
              </div>
            </div>

            {/* Hero Copy */}
            <div className="space-y-4 max-w-xl">
              <p className="text-xs font-mono font-semibold uppercase tracking-[0.24em] text-cyan-300/90 flex items-center gap-2">
                <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                Container Rate Intelligence Workspace
              </p>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-medium leading-[1.08] tracking-tight text-white drop-shadow-md">
                One shared desk for{" "}
                <span className="italic underline decoration-cyan-400/50 decoration-wavy underline-offset-8 text-cyan-200">
                  rate sourcing.
                </span>
              </h1>
              
              <p className="text-sm sm:text-base text-slate-300/80 leading-relaxed max-w-lg">
                Automated multi-carrier quote sourcing, instant contract benchmarking, and route reliability matrices across Maersk, CMA CGM, Hapag-Lloyd, MSC, ONE, and OOCL.
              </p>
            </div>

            {/* Carrier badges strip */}
            <div className="pt-2 flex items-center gap-2.5 flex-wrap">
              {["Maersk", "CMA CGM", "Hapag-Lloyd", "MSC", "ONE", "OOCL"].map((c) => (
                <span 
                  key={c}
                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-white/[0.06] text-white/70 border border-white/10 backdrop-blur-sm shadow-xs"
                >
                  {c}
                </span>
              ))}
            </div>
          </div>

          {/* Right Column: Auth Card */}
          <div className="lg:col-span-5 w-full">
            <div className="bg-slate-950/75 dark:bg-black/80 border border-white/15 backdrop-blur-2xl rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-2xl text-white relative overflow-hidden">
              {/* Subtle top inner glow */}
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent pointer-events-none" />

              {/* Tabs Switcher */}
              <div className="grid grid-cols-2 gap-1.5 p-1 bg-white/[0.06] border border-white/10 rounded-xl mb-6">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("login");
                    setErrorMessage("");
                  }}
                  className={`py-2.5 px-3 text-xs sm:text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                    activeTab === "login"
                      ? "bg-cyan-700/90 text-white shadow-md shadow-cyan-900/40"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <Lock className="size-3.5" />
                  Sign in
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("signup");
                    setErrorMessage("");
                  }}
                  className={`py-2.5 px-3 text-xs sm:text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                    activeTab === "signup"
                      ? "bg-cyan-700/90 text-white shadow-md shadow-cyan-900/40"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <UserPlus className="size-3.5" />
                  Request access
                </button>
              </div>

              {/* Banner alerts */}
              {errorMessage && (
                <div className="mb-5 p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs sm:text-sm flex items-start gap-2.5 animate-in fade-in slide-in-from-top-1">
                  <AlertCircle className="size-4 shrink-0 mt-0.5 text-rose-400" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {successMessage && (
                <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs sm:text-sm flex items-start gap-2.5 animate-in fade-in slide-in-from-top-1">
                  <CheckCircle2 className="size-4 shrink-0 mt-0.5 text-emerald-400" />
                  <span>{successMessage}</span>
                </div>
              )}

              {/* TAB 1: SIGN IN */}
              {activeTab === "login" && (
                <form onSubmit={handleLoginSubmit} className="space-y-4">
                  <div>
                    <h2 className="text-xl font-serif font-medium text-white mb-1">
                      Welcome back
                    </h2>
                    <p className="text-xs text-slate-400">
                      Sign in to your Infreight rate sourcing workspace.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Username
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        required
                        autoFocus
                        placeholder="e.g. brian"
                        value={loginUsername}
                        onChange={(e) => setLoginUsername(e.target.value)}
                        className="w-full h-11 pl-10 pr-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                      />
                      <User className="size-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold text-slate-300">
                        Password
                      </label>
                      <button
                        type="button"
                        onClick={() => {
                          setSetupUsername(loginUsername);
                          setActiveTab("setup");
                        }}
                        className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                      >
                        Legacy user? Set password
                      </button>
                    </div>
                    <div className="relative">
                      <input
                        type="password"
                        required
                        placeholder="••••••••"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        className="w-full h-11 pl-10 pr-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                      />
                      <Lock className="size-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !loginUsername.trim() || !loginPassword}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl shadow-lg shadow-cyan-900/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
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
                <form onSubmit={handleSignupSubmit} className="space-y-4">
                  <div>
                    <h2 className="text-xl font-serif font-medium text-white mb-1">
                      Request an account
                    </h2>
                    <p className="text-xs text-slate-400">
                      An administrator reviews every request. You can sign in once approved.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Full Name
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Brian Lee"
                      value={signupName}
                      onChange={(e) => setSignupName(e.target.value)}
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Username
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. brian.lee"
                      value={signupUsername}
                      onChange={(e) => setSignupUsername(e.target.value)}
                      pattern="[a-zA-Z0-9._-]{3,40}"
                      title="3–40 characters: letters, numbers, dot, dash, underscore"
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                    <p className="text-[11px] text-slate-400">
                      3–40 letters, numbers, dots, dashes or underscores.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Password
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      placeholder="At least 8 characters"
                      value={signupPassword}
                      onChange={(e) => setSignupPassword(e.target.value)}
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      placeholder="Confirm password"
                      value={signupConfirm}
                      onChange={(e) => setSignupConfirm(e.target.value)}
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !signupName.trim() || !signupUsername.trim() || !signupPassword}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl shadow-lg shadow-cyan-900/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="size-4 animate-spin" />
                        Submitting request…
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

              {/* TAB 3: SETUP NEW PASSWORD (FOR LEGACY USERS) */}
              {activeTab === "setup" && (
                <form onSubmit={handleSetupSubmit} className="space-y-4">
                  <div className="p-3.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-200 text-xs space-y-1">
                    <p className="font-semibold flex items-center gap-1.5 text-white">
                      <KeyRound className="size-3.5 text-amber-400" />
                      Mandatory Security Upgrade
                    </p>
                    <p className="text-slate-300">
                      All existing platform accounts must create a new secure password to continue sourcing freight rates.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Account Username or Name
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. brian"
                      value={setupUsername}
                      onChange={(e) => setSetupUsername(e.target.value)}
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      New Password
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      placeholder="At least 8 characters"
                      value={setupPasswordInput}
                      onChange={(e) => setSetupPasswordInput(e.target.value)}
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      placeholder="Confirm new password"
                      value={setupConfirmInput}
                      onChange={(e) => setSetupConfirmInput(e.target.value)}
                      className="w-full h-11 px-4 bg-black/50 border border-white/15 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 rounded-xl text-sm text-white placeholder:text-slate-500 outline-none transition-all"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !setupUsername.trim() || !setupPasswordInput}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl shadow-lg shadow-cyan-900/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="size-4 animate-spin" />
                        Updating password…
                      </>
                    ) : (
                      <>
                        Activate & Sign In
                        <ArrowRight className="size-4" />
                      </>
                    )}
                  </button>

                  <div className="text-center pt-2">
                    <button
                      type="button"
                      onClick={() => {
                        setActiveTab("login");
                        setErrorMessage("");
                      }}
                      className="text-xs text-slate-400 hover:text-white underline"
                    >
                      Return to Sign In
                    </button>
                  </div>
                </form>
              )}

              {/* Security badges footer */}
              <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span className="flex items-center gap-1">
                  <ShieldCheck className="size-3 text-cyan-400" />
                  scrypt KDF
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Lock className="size-3 text-cyan-400" />
                  SHA-256 Tokens
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Sparkles className="size-3 text-cyan-400" />
                  Internal Portal
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </SilkAurora>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">Loading…</div>}>
      <LoginContent />
    </Suspense>
  );
}
