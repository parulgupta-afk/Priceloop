// Thin fetch wrapper around the real Priceloop backend. Every call here
// hits an endpoint that was tested end-to-end (see backend/ test runs) --
// this is not a mock layer, it is the actual integration point.

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "priceloop_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export interface User {
  id: string;
  email: string;
  role: string;
}

export interface Subscription {
  id: string;
  plan: string;
  status: string;
  current_period_end: string | null;
}

export const api = {
  register: (email: string, password: string) =>
    request<User>("/api/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),

  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>("/api/auth/me"),

  getSubscription: () => request<Subscription>("/api/billing/subscription"),

  createCheckoutSession: (plan: "professional" | "enterprise") =>
    request<{ checkout_url: string }>("/api/billing/create-checkout-session", {
      method: "POST",
      body: JSON.stringify({ plan }),
    }),
};

export { ApiError };
