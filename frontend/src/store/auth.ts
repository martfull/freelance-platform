"use client";

import { create } from "zustand";
import { api } from "@/lib/api";
import { tokens } from "@/lib/tokens";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types/auth";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<User>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (data: LoginRequest) => {
    set({ isLoading: true });
    try {
      const { data: tokenData } = await api.post<TokenResponse>("/accounts/login", data);
      tokens.set(tokenData.access_token, tokenData.refresh_token);
      const { data: user } = await api.get<User>("/accounts/me");
      set({ user, isAuthenticated: true });
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (data: RegisterRequest) => {
    set({ isLoading: true });
    try {
      const { data: user } = await api.post<User>("/accounts/register", data);
      return user;
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    const refresh = tokens.getRefresh();
    if (refresh) {
      try {
        await api.post("/accounts/logout", { refresh_token: refresh });
      } catch {
        // ігноруємо помилку — все одно чистимо локальний стан
      }
    }
    tokens.clear();
    set({ user: null, isAuthenticated: false });
  },

  fetchMe: async () => {
    if (!tokens.hasRefresh()) return;
    set({ isLoading: true });
    try {
      const { data: user } = await api.get<User>("/accounts/me");
      set({ user, isAuthenticated: true });
    } catch {
      tokens.clear();
      set({ user: null, isAuthenticated: false });
    } finally {
      set({ isLoading: false });
    }
  },
}));
