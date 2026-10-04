<template>
  <view class="page">
    <view class="title">顾客登录</view>
    <input class="input" v-model="username" placeholder="用户名" />
    <input class="input" v-model="password" password placeholder="密码" />
    <button type="primary" @click="login">登录</button>
    <button @click="register">注册</button>
    <view class="hint">演示 user / user123</view>
  </view>
</template>

<script>
import { request } from "../../utils/api";

export default {
  data() {
    return { username: "user", password: "user123" };
  },
  methods: {
    async login() {
      try {
        const data = await request("/auth/login", "POST", {
          username: this.username,
          password: this.password,
        });
        uni.setStorageSync("token", data.access_token);
        uni.switchTab({ url: "/pages/menu/menu" });
      } catch (e) {
        uni.showToast({
          title: (e && e.detail) || "登录失败",
          icon: "none",
        });
      }
    },
    async register() {
      try {
        const data = await request("/auth/register", "POST", {
          username: this.username,
          password: this.password,
        });
        uni.setStorageSync("token", data.access_token);
        uni.switchTab({ url: "/pages/menu/menu" });
      } catch (e) {
        uni.showToast({ title: (e && e.detail) || "注册失败", icon: "none" });
      }
    },
  },
};
</script>

<style>
.page { padding: 40px 24px; }
.title { font-size: 24px; font-weight: 700; margin-bottom: 24px; }
.input {
  background: #fff;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}
.hint { color: #888; margin-top: 16px; font-size: 12px; }
</style>
