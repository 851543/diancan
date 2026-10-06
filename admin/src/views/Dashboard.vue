<template>
  <div>
    <h3>今日概览</h3>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-statistic title="订单数" :value="stats.total" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="待处理" :value="stats.pendingLike" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="营业额（元）" :value="stats.revenueYuan" :precision="2" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../api";

const PENDING_LIKE = new Set(["pending", "paid", "preparing", "ready"]);
const stats = ref({ total: 0, pendingLike: 0, revenueYuan: 0 });

function summarizeOrders(orders) {
  const list = orders || [];
  const pendingLike = list.filter((o) => PENDING_LIKE.has(o.status)).length;
  const revenueCents = list
    .filter((o) => o.status === "completed")
    .reduce((sum, o) => sum + (o.total_cents || 0), 0);
  return {
    total: list.length,
    pendingLike,
    revenueYuan: revenueCents / 100,
  };
}

function isToday(iso) {
  const d = new Date(iso);
  const now = new Date();
  return d.toDateString() === now.toDateString();
}

onMounted(async () => {
  const { data } = await http.get("/orders/admin");
  stats.value = summarizeOrders((data || []).filter((o) => isToday(o.created_at)));
});
</script>
