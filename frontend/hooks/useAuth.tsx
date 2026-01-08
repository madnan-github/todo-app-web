"use client";

import type { SignUpFormData, SignInFormData } from "@/types";
import { useState, useEffect, useCallback, createContext, useContext, ReactNode } from "react";
import { authClient } from "@/lib/auth";

// Types for our auth context
interface User {
  id: string;
  email: string;
  name: string;
  image?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  signIn: (data: SignInFormData) => Promise<void>;
  signUp: (data: SignUpFormData) => Promise<void>;
  signOut: () => Promise<void>;
}

// Create auth context
const AuthContext = createContext<AuthContextType | null>(null);

// Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sync state with Better Auth client
  const { data: session, isPending, error: authError } = authClient.useSession();

  useEffect(() => {
    // Set a timeout to prevent infinite loading state
    const timeoutId = setTimeout(() => {
      if (isLoading) {
        console.warn('[useAuth] Session check timed out, setting isLoading to false');
        setIsLoading(false);
      }
    }, 3000); // 3 second timeout

    if (!isPending) {
      clearTimeout(timeoutId);
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email,
          name: session.user.name || "",
          image: session.user.image || undefined,
        });
      } else {
        setUser(null);
      }
      setIsLoading(false);
    }

    return () => clearTimeout(timeoutId);
  }, [session, isPending, isLoading]);

  useEffect(() => {
    if (authError) {
      setError(authError.message || "Authentication error");
    }
  }, [authError]);

  const signInWithEmail = useCallback(async (data: SignInFormData) => {
    setError(null);
    setIsLoading(true);
    try {
      const { error } = await authClient.signIn.email({
        email: data.email,
        password: data.password,
      });

      if (error) {
        throw new Error(error.message || "Sign in failed");
      }
    } catch (err: any) {
      setError(err.message || "Sign in failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signUpWithEmail = useCallback(async (data: SignUpFormData) => {
    setError(null);
    setIsLoading(true);
    try {
      const { error } = await authClient.signUp.email({
        email: data.email,
        password: data.password,
        name: data.name,
      });

      if (error) {
        throw new Error(error.message || "Sign up failed");
      }
    } catch (err: any) {
      setError(err.message || "Sign up failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    try {
      await authClient.signOut();
      setUser(null);
    } catch (err: any) {
      setError(err.message || "Sign out failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        signIn: signInWithEmail,
        signUp: signUpWithEmail,
        signOut: logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
