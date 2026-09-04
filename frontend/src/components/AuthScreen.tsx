import React, { useState } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const AuthScreen: React.FC = () => {
  const { login, register, error } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
    } catch {
      // error is already surfaced via context.error
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8f9ff] flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-[#0b1c30] mb-1">Priceloop</h1>
          <p className="text-sm text-[#64748b]">
            {mode === "login" ? "Log in to your account" : "Create your account"}
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-[#e2e8f0] shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#475569] mb-1.5">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full px-3 py-2.5 rounded-lg border border-[#e2e8f0] text-sm text-[#0b1c30] focus:outline-none focus:ring-2 focus:ring-[#0051d5]/30 focus:border-[#0051d5]"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[#475569] mb-1.5">Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="********"
                className="w-full px-3 py-2.5 rounded-lg border border-[#e2e8f0] text-sm text-[#0b1c30] focus:outline-none focus:ring-2 focus:ring-[#0051d5]/30 focus:border-[#0051d5]"
              />
            </div>

            {error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#0051d5] hover:bg-[#0042b0] disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {mode === "login" ? "Log in" : "Create account"}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-[#64748b] mt-4">
          {mode === "login" ? "New here? " : "Already have an account? "}
          <button
            onClick={() => setMode(mode === "login" ? "signup" : "login")}
            className="text-[#0051d5] font-medium hover:underline"
          >
            {mode === "login" ? "Sign up" : "Log in"}
          </button>
        </p>
      </div>
    </div>
  );
};
