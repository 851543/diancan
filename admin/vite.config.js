import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://127.0.0.1:8000",
      "/dishes": "http://127.0.0.1:8000",
      "/orders": "http://127.0.0.1:8000",
      "/cart": "http://127.0.0.1:8000",
    },
  },
});
