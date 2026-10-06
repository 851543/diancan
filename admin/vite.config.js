import path from "path";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig(({ mode }) => {
  const root = path.resolve(__dirname, "..");
  const env = loadEnv(mode, root, "VITE_");
  const api = (env.VITE_API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");

  return {
    envDir: root,
    plugins: [vue()],
    server: {
      port: 5173,
      proxy: {
        "/auth": { target: api, changeOrigin: true },
        "/dishes": { target: api, changeOrigin: true },
        "/orders": { target: api, changeOrigin: true },
        "/cart": { target: api, changeOrigin: true },
      },
    },
  };
});
