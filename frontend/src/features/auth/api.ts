export interface CurrentUser {
  id: string;
  email: string;
  display_name: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, { credentials: "include" });
  if (res.status === 401) return null;
  if (!res.ok) throw new Error("Failed to fetch current user");
  return res.json();
}

export function loginUrl(): string {
  return `${API_BASE_URL}/api/v1/auth/login`;
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}