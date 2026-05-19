import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { tokens } from "./tokens";
import type { TokenResponse } from "@/types/auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost/api";

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Додає Bearer токен до кожного запиту
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokens.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// При 401 — пробує refresh, потім повторює запит
let isRefreshing = false;
let waitQueue: Array<(token: string) => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    const refreshToken = tokens.getRefresh();
    if (!refreshToken) {
      tokens.clear();
      if (typeof window !== "undefined") window.location.href = "/login";
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        waitQueue.push((newToken: string) => {
          original.headers.Authorization = `Bearer ${newToken}`;
          resolve(api(original));
        });
      });
    }

    original._retry = true;
    isRefreshing = true;

    try {
      const { data } = await axios.post<TokenResponse>(
        `${BASE_URL}/accounts/refresh`,
        { refresh_token: refreshToken }
      );
      tokens.set(data.access_token, data.refresh_token);
      waitQueue.forEach((cb) => cb(data.access_token));
      waitQueue = [];
      original.headers.Authorization = `Bearer ${data.access_token}`;
      return api(original);
    } catch {
      tokens.clear();
      waitQueue = [];
      if (typeof window !== "undefined") window.location.href = "/login";
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  }
);
