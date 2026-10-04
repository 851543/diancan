/**
 * H5 开发：空字符串，走 manifest / Vite 代理到后端。
 * App / 真机：用 VITE_API_BASE（项目根目录 .env），例如 http://192.168.1.8:8000
 */
function resolveBaseUrl() {
  const fromEnv = String(import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");
  // #ifdef H5
  return "";
  // #endif
  return fromEnv || "http://127.0.0.1:8000";
}

export const BASE_URL = resolveBaseUrl();

export function request(url, method, data) {
  const token = uni.getStorageSync("token");
  const path = url.startsWith("/") ? url : `/${url}`;
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${path}`,
      method,
      data,
      header: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: "Bearer " + token } : {}),
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data);
        else {
          if (res.statusCode === 401) {
            uni.removeStorageSync("token");
            uni.navigateTo({ url: "/pages/login/login" });
          }
          reject(res.data);
        }
      },
      fail: (err) => {
        console.error("请求失败", method, `${BASE_URL}${path}`, err);
        reject(err);
      },
    });
  });
}
