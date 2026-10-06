import axios from "axios";

const http = axios.create({
  baseURL: import.meta.env.DEV
    ? ""
    : String(import.meta.env.VITE_API_BASE || "").replace(/\/$/, ""),
});

function isAuthRequest(url = "") {
  return url.includes("/auth/login") || url.includes("/auth/register");
}

export function errorText(data, fallback = "请求失败") {
  const d = data?.detail;
  if (typeof d === "string" && d) return d;
  if (Array.isArray(d) && d[0]?.msg) return d[0].msg;
  return fallback;
}

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || "";
    if (err.response?.status === 401 && !isAuthRequest(url)) {
      localStorage.removeItem("token");
      if (location.pathname !== "/login") location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default http;
