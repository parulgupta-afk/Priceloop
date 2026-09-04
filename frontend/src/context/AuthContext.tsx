import React, { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken, clearToken, User, ApiError } from "../lib/api";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // On mount: if a token is already stored, validate it against the real
  // backend (GET /api/auth/me) rather than trusting it blindly. If the
  // backend rejects it (expired/tampered), drop it and show the login screen.
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    setError(null);
    try {
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      const me = await api.me();
      setUser(me);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Login failed. Please try again.");
      throw e;
    }
  };

  const register = async (email: string, password: string) => {
    setError(null);
    try {
      await api.register(email, password);
      // Registration succeeded but does not log the user in by itself --
      // log in right after with the same credentials for a one-step signup flow.
      await login(email, password);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not create account.");
      throw e;
    }
  };

  const logout = () => {
    clearToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, error, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
