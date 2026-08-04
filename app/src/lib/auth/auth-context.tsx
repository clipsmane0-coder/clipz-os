// ============================================================
// CLIPZ — Auth Context
// ============================================================

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import * as authApi from "../api/auth";

const TOKEN_KEY = "clipz-auth-token";
const USER_KEY = "clipz-auth-user";

interface AuthState {
  user: authApi.AuthUser | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, displayName: string) => Promise<void>;
  signOut: () => Promise<void>;
  signInWithGoogle: (credential: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function loadStoredAuth(): { token: string | null; user: authApi.AuthUser | null } {
  if (typeof window === "undefined") return { token: null, user: null };
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const user = localStorage.getItem(USER_KEY);
    return {
      token,
      user: user ? JSON.parse(user) : null,
    };
  } catch {
    return { token: null, user: null };
  }
}

function storeAuth(token: string, user: authApi.AuthUser) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearAuth() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const stored = loadStoredAuth();
    return {
      user: stored.user,
      token: stored.token,
      isLoading: false,
      isAuthenticated: !!stored.token && !!stored.user,
    };
  });

  // Verify session on mount
  useEffect(() => {
    const stored = loadStoredAuth();
    if (!stored.token) return;

    // Validate the token is still valid
    authApi.getMe(stored.token)
      .then((res) => {
        setState({
          user: res.data,
          token: stored.token,
          isLoading: false,
          isAuthenticated: true,
        });
        storeAuth(stored.token, res.data);
      })
      .catch(() => {
        // Token expired or invalid
        clearAuth();
        setState({ user: null, token: null, isLoading: false, isAuthenticated: false });
      });
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    setState((s) => ({ ...s, isLoading: true }));
    try {
      const res = await authApi.login(email, password);
      const { token, user } = res.data;
      storeAuth(token, user);
      setState({ user, token, isLoading: false, isAuthenticated: true });
    } catch (err) {
      setState((s) => ({ ...s, isLoading: false }));
      throw err;
    }
  }, []);

  const signUp = useCallback(async (email: string, password: string, displayName: string) => {
    setState((s) => ({ ...s, isLoading: true }));
    try {
      const res = await authApi.register(email, password, displayName);
      const { token, user } = res.data;
      storeAuth(token, user);
      setState({ user, token, isLoading: false, isAuthenticated: true });
    } catch (err) {
      setState((s) => ({ ...s, isLoading: false }));
      throw err;
    }
  }, []);

  const signOut = useCallback(async () => {
    const stored = loadStoredAuth();
    if (stored.token) {
      try {
        await authApi.logout(stored.token);
      } catch {
        // Ignore errors during logout
      }
    }
    clearAuth();
    setState({ user: null, token: null, isLoading: false, isAuthenticated: false });
  }, []);

  const signInWithGoogle = useCallback(async (credential: string) => {
    setState((s) => ({ ...s, isLoading: true }));
    try {
      const res = await authApi.googleAuth(credential);
      const { token, user } = res.data;
      storeAuth(token, user);
      setState({ user, token, isLoading: false, isAuthenticated: true });
    } catch (err) {
      setState((s) => ({ ...s, isLoading: false }));
      throw err;
    }
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, signIn, signUp, signOut, signInWithGoogle }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}