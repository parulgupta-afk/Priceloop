import React, { useState } from "react";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ShieldCheck,
  Loader2,
  Zap,
  TrendingUp,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const AuthScreen: React.FC = () => {
  const { login, register, error: serverError } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotEmailSent, setForgotEmailSent] = useState(false);

  // Quick fill demo credentials
  const handleFillDemo = () => {
    setEmail("demo@priceloop.ai");
    setPassword("demo12345");
    setLocalError(null);
  };

  // Password strength calculation
  const getPasswordStrength = () => {
    if (!password) return 0;
    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    return score;
  };

  const passwordStrength = getPasswordStrength();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    // Validation
    if (!email || !email.includes("@")) {
      setLocalError("Please provide a valid email address.");
      return;
    }

    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters long.");
      return;
    }

    if (mode === "signup" && password !== confirmPassword) {
      setLocalError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
    } catch {
      // serverError from context is surfaced
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayError = localError || serverError;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center px-4 py-8 relative overflow-hidden selection:bg-blue-500 selection:text-white">
      {/* Background Ambient Glow & Grid Accent */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(59,130,246,0.18),transparent_50%)] pointer-events-none" />
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(#94a3b8 1px, transparent 1px)`,
          backgroundSize: "24px 24px",
        }}
      />

      <div className="w-full max-w-[460px] relative z-10">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-13 h-13 rounded-2xl bg-gradient-to-tr from-blue-600 via-blue-500 to-indigo-500 p-0.5 shadow-lg shadow-blue-500/25 mb-3.5">
            <div className="w-full h-full bg-slate-950/40 rounded-[14px] flex items-center justify-center backdrop-blur-xs">
              <TrendingUp className="w-7 h-7 text-blue-400 drop-shadow" />
            </div>
          </div>
          <div className="flex items-center justify-center gap-2 mb-1">
            <h1 className="text-2xl font-bold tracking-tight text-white font-sans">
              Priceloop
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-blue-500/15 border border-blue-500/30 text-blue-400 rounded-full">
              AI Market Intel
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-xs mx-auto">
            {mode === "login"
              ? "Autonomous pricing intelligence & real-time competitor tracking"
              : "Start monitoring competitors and maximizing margins in minutes"}
          </p>
        </div>

        {/* Card Container */}
        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl shadow-black/60 p-6 sm:p-8 transition-all">
          {/* Segmented Tab Controls */}
          <div className="grid grid-cols-2 p-1 bg-slate-950/60 border border-slate-800/80 rounded-xl mb-6">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setLocalError(null);
              }}
              className={`py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                mode === "login"
                  ? "bg-blue-600 text-white shadow-sm shadow-blue-500/25"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
              }`}
            >
              <span>Sign In</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("signup");
                setLocalError(null);
              }}
              className={`py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                mode === "signup"
                  ? "bg-blue-600 text-white shadow-sm shadow-blue-500/25"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-300" />
              <span>Create Account</span>
            </button>
          </div>

          {/* Error Alert */}
          {displayError && (
            <div className="mb-5 flex items-start gap-2.5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs animate-fade-in">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
              <div className="flex-1 leading-relaxed">{displayError}</div>
              <button
                type="button"
                onClick={() => setLocalError(null)}
                className="text-rose-400/80 hover:text-rose-300 text-sm leading-none ml-1 cursor-pointer"
                aria-label="Dismiss error"
              >
                &times;
              </button>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-3.5 py-2.5 bg-slate-950/70 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-slate-300">
                  Password
                </label>
                {mode === "login" && (
                  <button
                    type="button"
                    onClick={() => {
                      setShowForgotPassword(!showForgotPassword);
                      setForgotEmailSent(false);
                    }}
                    className="text-[11px] text-blue-400 hover:text-blue-300 transition-colors font-medium cursor-pointer"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full pl-10 pr-10 py-2.5 bg-slate-950/70 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>

              {/* Password strength meter for Signup */}
              {mode === "signup" && password && (
                <div className="mt-2 space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Password strength</span>
                    <span
                      className={`font-medium ${
                        passwordStrength <= 1
                          ? "text-rose-400"
                          : passwordStrength <= 2
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {passwordStrength <= 1
                        ? "Weak"
                        : passwordStrength <= 2
                        ? "Fair"
                        : passwordStrength === 3
                        ? "Good"
                        : "Strong"}
                    </span>
                  </div>
                  <div className="grid grid-cols-4 gap-1 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        passwordStrength >= 1 ? "bg-rose-500" : "bg-transparent"
                      }`}
                    />
                    <div
                      className={`h-full rounded-full transition-all ${
                        passwordStrength >= 2 ? "bg-amber-500" : "bg-transparent"
                      }`}
                    />
                    <div
                      className={`h-full rounded-full transition-all ${
                        passwordStrength >= 3 ? "bg-blue-500" : "bg-transparent"
                      }`}
                    />
                    <div
                      className={`h-full rounded-full transition-all ${
                        passwordStrength >= 4 ? "bg-emerald-500" : "bg-transparent"
                      }`}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password Field for Signup */}
            {mode === "signup" && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    required
                    autoComplete="new-password"
                    minLength={8}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat your password"
                    className={`w-full pl-10 pr-10 py-2.5 bg-slate-950/70 border rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none transition-all ${
                      confirmPassword && confirmPassword !== password
                        ? "border-rose-500/70 focus:ring-2 focus:ring-rose-500/20"
                        : confirmPassword && confirmPassword === password
                        ? "border-emerald-500/70 focus:ring-2 focus:ring-emerald-500/20"
                        : "border-slate-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                    aria-label={
                      showConfirmPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
                {confirmPassword && confirmPassword === password && (
                  <p className="flex items-center gap-1 text-[11px] text-emerald-400 mt-1.5">
                    <CheckCircle2 className="w-3 h-3" /> Passwords match
                  </p>
                )}
              </div>
            )}

            {/* Forgot password collapsible helper */}
            {showForgotPassword && mode === "login" && (
              <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs space-y-2">
                <p className="text-slate-300 font-medium">Reset Password</p>
                {forgotEmailSent ? (
                  <p className="text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    Reset link sent to {email || "your email"}.
                  </p>
                ) : (
                  <>
                    <p className="text-slate-400 text-[11px]">
                      Enter your email above and click below to request a secure password recovery link.
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        if (!email) {
                          setLocalError("Please enter your email address first.");
                          return;
                        }
                        setForgotEmailSent(true);
                      }}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors cursor-pointer"
                    >
                      Send Reset Instructions
                    </button>
                  </>
                )}
              </div>
            )}

            {/* Remember Me Checkbox */}
            {mode === "login" && (
              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded bg-slate-950 border-slate-700 text-blue-600 focus:ring-blue-500/20 focus:ring-offset-slate-900"
                  />
                  <span className="text-xs text-slate-300">
                    Stay logged in for 30 days
                  </span>
                </label>
              </div>
            )}

            {/* Sign Up Terms */}
            {mode === "signup" && (
              <p className="text-[11px] text-slate-400 leading-relaxed pt-1">
                By creating an account, you agree to our{" "}
                <span className="text-blue-400 hover:underline cursor-pointer">
                  Terms of Service
                </span>{" "}
                and{" "}
                <span className="text-blue-400 hover:underline cursor-pointer">
                  Privacy Policy
                </span>
                .
              </p>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full relative group overflow-hidden bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-60 text-white font-medium py-2.5 px-4 rounded-xl shadow-lg shadow-blue-600/20 hover:shadow-blue-500/30 transition-all text-sm flex items-center justify-center gap-2 mt-2 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>
                    {mode === "login"
                      ? "Signing you in..."
                      : "Setting up your account..."}
                  </span>
                </>
              ) : (
                <>
                  <span>
                    {mode === "login" ? "Sign In to Dashboard" : "Create My Account"}
                  </span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Demo account quick login chip */}
          {mode === "login" && (
            <div className="mt-5 pt-4 border-t border-slate-800/80">
              <button
                type="button"
                onClick={handleFillDemo}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/40 text-xs text-slate-400 hover:text-slate-200 transition-all group cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  <span>Fill Demo Credentials</span>
                </div>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md group-hover:bg-slate-700 font-mono">
                  demo@priceloop.ai
                </span>
              </button>
            </div>
          )}
        </div>

        {/* Mode Switch Footer */}
        <div className="text-center mt-5">
          <p className="text-xs text-slate-400">
            {mode === "login" ? (
              <>
                Don&apos;t have an account yet?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setMode("signup");
                    setLocalError(null);
                  }}
                  className="text-blue-400 font-semibold hover:text-blue-300 hover:underline transition-colors cursor-pointer"
                >
                  Create one now
                </button>
              </>
            ) : (
              <>
                Already registered?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setMode("login");
                    setLocalError(null);
                  }}
                  className="text-blue-400 font-semibold hover:text-blue-300 hover:underline transition-colors cursor-pointer"
                >
                  Sign in here
                </button>
              </>
            )}
          </p>
        </div>

        {/* Trust Badges */}
        <div className="flex items-center justify-center gap-6 mt-8 text-[11px] text-slate-500">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
            <span>256-bit SSL Encryption</span>
          </div>
          <span className="w-1 h-1 rounded-full bg-slate-700" />
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-slate-400" />
            <span>Real-time Sync</span>
          </div>
        </div>
      </div>
    </div>
  );
};
