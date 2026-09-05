"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [message, setMessage] = useState("");
  const [token, setToken] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");

    try {
      if (mode === "register") {
        const res = await fetch(`${API}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Registration failed");
        }
        setMessage("Registered successfully. You can now log in.");
        setMode("login");
        return;
      }

      // OAuth2 password form
      const body = new URLSearchParams();
      body.set("username", email);
      body.set("password", password);

      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Login failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem("priceloop_token", data.access_token);
      setMessage("Logged in. Token stored in localStorage.");
    } catch (err: any) {
      setMessage(err.message || "Something went wrong");
    }
  }

  return (
    <div style={{ maxWidth: 420 }}>
      <h1>{mode === "login" ? "Login" : "Register"}</h1>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
          <button type="submit">
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: "1rem" }}>
          {mode === "login" ? (
            <>
              No account?{" "}
              <button
                type="button"
                className="btn"
                style={{ background: "transparent", color: "var(--accent)" }}
                onClick={() => setMode("register")}
              >
                Register
              </button>
            </>
          ) : (
            <>
              Have an account?{" "}
              <button
                type="button"
                className="btn"
                style={{ background: "transparent", color: "var(--accent)" }}
                onClick={() => setMode("login")}
              >
                Login
              </button>
            </>
          )}
        </p>
        {message && <p style={{ marginTop: "0.75rem" }}>{message}</p>}
        {token && (
          <p className="muted" style={{ wordBreak: "break-all", fontSize: 12 }}>
            Token: {token.slice(0, 24)}…
          </p>
        )}
      </div>
    </div>
  );
}
