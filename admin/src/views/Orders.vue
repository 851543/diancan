<template>
  <div>
    <h3>订单</h3>
    <el-table :data="rows" stripe>
      <el-table-column prop="id" label="单号" width="80" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">{{ statusText(row.status) }}</template>
      </el-table-column>
      <el-table-column label="金额" width="120">
        <template #default="{ row }">{{ (row.total_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="菜品">
        <template #default="{ row }">
          {{ row.items.map((i) => `${i.name} x${i.qty}`).join("、") }}
        </template>
      </el-table-column>
      <el-table-column label="流转" width="280">
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

function statusText(status) {
  return statusMap[status] || status;
}

function nextOf(status) {
  return flow[status] || "";
}

async function load() {
  rows.value = (await http.get("/orders/admin")).data;
}

async function setStatus(row, status) {
  try {
    await http.patch(`/orders/admin/${row.id}`, { status });
    ElMessage.success("已更新");
    load();
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || "失败");
  }
}

onMounted(load);
</script>
