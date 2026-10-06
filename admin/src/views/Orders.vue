<template>
  <div>
    <div class="bar">
      <h3>订单</h3>
      <el-radio-group v-model="status" @change="load">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="pending">待支付</el-radio-button>
        <el-radio-button label="paid">已支付</el-radio-button>
        <el-radio-button label="preparing">制作中</el-radio-button>
        <el-radio-button label="ready">待取餐</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
        <el-radio-button label="cancelled">已取消</el-radio-button>
      </el-radio-group>
    </div>
    <el-table :data="rows" stripe>
      <el-table-column prop="id" label="单号" width="80" />
      <el-table-column prop="username" label="顾客" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">{{ statusText(row.status) }}</template>
      </el-table-column>
      <el-table-column label="金额" width="100">
        <template #default="{ row }">{{ (row.total_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="菜品" min-width="180">
        <template #default="{ row }">
          {{ row.items.map((i) => `${i.name} x${i.qty}`).join("、") }}
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" width="140" />
      <el-table-column label="时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="流转" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="setStatus(row, nextOf(row.status))" :disabled="!nextOf(row.status)">
            下一步
          </el-button>
          <el-button
            size="small"
            @click="setStatus(row, 'cancelled')"
            :disabled="row.status === 'completed' || row.status === 'cancelled'"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api";

const rows = ref([]);
const status = ref("");
const flow = {
  pending: "paid",
  paid: "preparing",
  preparing: "ready",
  ready: "completed",
};

const statusMap = {
  pending: "待支付",
  paid: "已支付",
  preparing: "制作中",
  ready: "待取餐",
  completed: "已完成",
  cancelled: "已取消",
};

function statusText(s) {
  return statusMap[s] || s;
}

function nextOf(s) {
  return flow[s] || "";
}

function formatTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

async function load() {
  const params = status.value ? { status: status.value } : {};
  rows.value = (await http.get("/orders/admin", { params })).data;
}

async function setStatus(row, next) {
  try {
    await http.patch(`/orders/admin/${row.id}`, { status: next });
    ElMessage.success("已更新");
    load();
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || "失败");
  }
}

onMounted(load);
</script>

<style scoped>
.bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
