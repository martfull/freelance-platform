// Access token живе тільки в пам'яті — не доступний через JS після перезавантаження
// Refresh token в localStorage — щоб відновити сесію після перезавантаження

const REFRESH_KEY = "refresh_token";

let _accessToken: string | null = null;

export const tokens = {
  getAccess: (): string | null => _accessToken,

  getRefresh: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(REFRESH_KEY);
  },

  set: (access: string, refresh: string): void => {
    _accessToken = access;
    if (typeof window !== "undefined") {
      localStorage.setItem(REFRESH_KEY, refresh);
      // cookie для middleware (не httpOnly — Next.js middleware читає тільки cookie)
      document.cookie = `refresh_token=${refresh}; path=/; SameSite=Lax; max-age=${7 * 24 * 3600}`;
    }
  },

  clear: (): void => {
    _accessToken = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem(REFRESH_KEY);
      document.cookie = "refresh_token=; path=/; max-age=0";
    }
  },

  hasRefresh: (): boolean => {
    if (typeof window === "undefined") return false;
    return !!localStorage.getItem(REFRESH_KEY);
  },
};
