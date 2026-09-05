import { api, clearTokens, isAuthenticated } from './client';

export interface UserOut {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export async function login(email: string, password: string) {
  return api.loginForm(email, password);
}

export async function register(email: string, password: string, fullName?: string) {
  return api.post<UserOut>('/auth/register', {
    email,
    password,
    full_name: fullName || null,
  });
}

export async function getMe(): Promise<UserOut | null> {
  if (!isAuthenticated()) return null;
  try {
    // Backend may not expose /me — try products as health of token
    await api.get('/products?limit=1');
    return { id: 'me', email: 'authenticated', full_name: null, role: 'USER', is_active: true, is_verified: true, created_at: '' };
  } catch {
    clearTokens();
    return null;
  }
}

export function logout() {
  clearTokens();
}

/** Demo credentials created by backend/scripts/seed_demo.py */
export const DEMO_CREDENTIALS = {
  email: 'demo@priceloop.local',
  password: 'demo12345',
};
