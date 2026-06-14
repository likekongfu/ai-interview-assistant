const API_BASE_URL = normalizeBaseUrl(
  process.env.NEXT_PUBLIC_API_BASE_URL || "/api"
);

type RequestOptions = Omit<RequestInit, "headers"> & {
  token?: string | null;
  headers?: Record<string, string>;
};

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { headers, ...rest } = options;

  const response = await apiFetch(path, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = getErrorMessage(data, response.status);
    throw new Error(message);
  }

  return data as T;
}

export function apiFetch(
  path: string,
  options: RequestOptions = {}
): Promise<Response> {
  const { token, headers, ...rest } = options;

  return fetch(buildApiUrl(path), {
    ...rest,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });
}

export function buildApiUrl(path: string) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

export { API_BASE_URL };

function getErrorMessage(data: unknown, status: number) {
  if (isRecord(data)) {
    if (typeof data.message === "string") return data.message;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const firstDetail = data.detail[0];
      if (isRecord(firstDetail) && typeof firstDetail.msg === "string") {
        return firstDetail.msg;
      }
    }
  }

  return `请求失败，状态码：${status}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function normalizeBaseUrl(value: string) {
  const trimmed = value.trim();
  if (!trimmed || trimmed === "/") return "";
  return trimmed.replace(/\/+$/, "");
}
