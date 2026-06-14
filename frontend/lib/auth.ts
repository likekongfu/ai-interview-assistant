export type CurrentUser = {
  token: string;
  username: string;
  userId: string;
};

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function getCurrentUser(): CurrentUser | null {
  if (typeof window === "undefined") return null;

  const token = localStorage.getItem("token");
  const username = localStorage.getItem("username");
  const userId = localStorage.getItem("user_id");

  if (!token || !username || !userId) return null;

  return { token, username, userId };
}

export function saveSession(session: {
  token: string;
  username: string;
  user_id: number;
}) {
  localStorage.setItem("token", session.token);
  localStorage.setItem("username", session.username);
  localStorage.setItem("user_id", String(session.user_id));
  window.dispatchEvent(new Event("auth-change"));
}

export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  localStorage.removeItem("user_id");
  window.dispatchEvent(new Event("auth-change"));
}
