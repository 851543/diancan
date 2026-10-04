<template>
  <div class="wrap">
    <el-card style="width: 360px">
      <h2>商家登录</h2>
      <el-form @submit.prevent="onSubmit">
        <el-form-item label="账号">
          <el-input v-model="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">
          登录
        </el-button>
        <p class="hint">演示账号 admin / admin123</p>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import http from "../api";

const router = useRouter();
const username = ref("admin");
const password = ref("admin123");
const loading = ref(false);

async function onSubmit() {
  loading.value = true;
  try {
    const { data } = await http.post("/auth/login", {
      username: username.value,
      password: password.value,
    });
    if (data.role !== "admin") {
      ElMessage.error("请用店员账号登录后台");
      return;
    }
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("username", data.username);
    router.push("/");
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || "登录失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.hint {
  color: #888;
  font-size: 12px;
  margin-top: 12px;
}
</style>
