const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const AUTH_STORAGE_KEY = "pulsestack-auth";

export function getStoredSession() {
  const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function saveStoredSession(session) {
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearStoredSession() {
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

function formatErrorDetail(detail) {
  if (!detail) {
    return "Request failed.";
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg || item.message || JSON.stringify(item))
      .join(", ");
  }

  if (typeof detail === "object") {
    return detail.message || JSON.stringify(detail);
  }

  return String(detail);
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options.headers,
    },
    method: options.method ?? "GET",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const raw = await response.text();
  const data = raw ? JSON.parse(raw) : {};
  if (!response.ok) {
    throw new Error(formatErrorDetail(data.detail));
  }

  return data;
}

export function loginRequest(credentials) {
  return request("/api/auth/login", {
    method: "POST",
    body: credentials,
  });
}

export function signupRequest(account) {
  return request("/api/auth/signup", {
    method: "POST",
    body: account,
  });
}

export function meRequest(token) {
  return request("/api/auth/me", { token });
}

export function logoutRequest(token) {
  return request("/api/auth/logout", {
    method: "POST",
    token,
  });
}

export function dashboardOverviewRequest(token) {
  return request("/api/dashboard/overview", { token });
}

export function analyticsOverviewRequest(token) {
  return request("/api/analytics/overview", { token });
}

export function usersOverviewRequest(token) {
  return request("/api/users/overview", { token });
}

export function reportsOverviewRequest(token) {
  return request("/api/reports/overview", { token });
}

export function billingOverviewRequest(token) {
  return request("/api/billing/overview", { token });
}

export function notificationsOverviewRequest(token) {
  return request("/api/notifications/overview", { token });
}

export function settingsOverviewRequest(token) {
  return request("/api/settings/overview", { token });
}

export function profileOverviewRequest(token) {
  return request("/api/profile/overview", { token });
}

export function createWorkspaceUserRequest(token, payload) {
  return request("/api/users/members", {
    method: "POST",
    token,
    body: payload,
  });
}

export function deleteWorkspaceUserRequest(token, memberId) {
  return request(`/api/users/members/${memberId}`, {
    method: "DELETE",
    token,
  });
}

export function createBillingItemRequest(token, payload) {
  return request("/api/billing/items", {
    method: "POST",
    token,
    body: payload,
  });
}

export function deleteBillingItemRequest(token, itemId) {
  return request(`/api/billing/items/${itemId}`, {
    method: "DELETE",
    token,
  });
}

export function createReportRunRequest(token, payload) {
  return request("/api/reports/runs", {
    method: "POST",
    token,
    body: payload,
  });
}

export function deleteReportRunRequest(token, reportId) {
  return request(`/api/reports/runs/${reportId}`, {
    method: "DELETE",
    token,
  });
}

export function createNotificationItemRequest(token, payload) {
  return request("/api/notifications/items", {
    method: "POST",
    token,
    body: payload,
  });
}

export function deleteNotificationItemRequest(token, notificationId) {
  return request(`/api/notifications/items/${notificationId}`, {
    method: "DELETE",
    token,
  });
}
