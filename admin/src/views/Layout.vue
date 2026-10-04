<template>
  <el-container style="min-height: 100vh">
    <el-aside width="200px" style="background: #1d1e1f; color: #fff">
      <div style="padding: 20px; font-weight: 700">点餐后台</div>
      <el-menu
        router
        :default-active="$route.path"
        background-color="#1d1e1f"
        text-color="#ddd"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/">概览</el-menu-item>
        <el-menu-item index="/dishes">菜单</el-menu-item>
        <el-menu-item index="/orders">订单</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display: flex; align-items: center; justify-content: space-between">
        <span>{{ username }}（店员）</span>
        <el-button @click="logout">退出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
const username = localStorage.getItem("username") || "";

function logout() {
  localStorage.clear();
  router.push("/login");
}
</script>
