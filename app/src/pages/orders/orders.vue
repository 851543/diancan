<template>
  <view class="page">
    <view class="top">
      <text>我的订单</text>
      <text class="logout" @click="logout">退出</text>
    </view>
    <view v-for="o in orders" :key="o.id" class="card">
      <view class="row">
        <text>#{{ o.id }}</text>
        <text>{{ statusText(o.status) }}</text>
      </view>
      <view v-for="i in o.items" :key="i.dish_id + '-' + i.name">{{ i.name }} × {{ i.qty }}</view>
      <view class="remark" v-if="o.remark">备注：{{ o.remark }}</view>
      <view class="price">¥ {{ yuan(o.total_cents) }}</view>
      <view class="actions" v-if="o.status === 'pending'">
        <button size="mini" @click="setStatus(o, 'cancelled')">取消</button>
        <button size="mini" type="primary" @click="setStatus(o, 'paid')">去支付</button>
      </view>
    </view>
    <view v-if="!orders.length" class="empty">暂无订单</view>
  </view>
</template>

<script>
import { request } from "../../utils/api";
import { yuan } from "../../utils/price";

export default {
  data() {
    return { orders: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    yuan,
    statusText(status) {
      return (
        {
          pending: "待支付",
          paid: "已支付",
          preparing: "制作中",
          ready: "待取餐",
          completed: "已完成",
          cancelled: "已取消",
        }[status] || status
      );
    },
    async load() {
      if (!uni.getStorageSync("token")) {
        uni.navigateTo({ url: "/pages/login/login" });
        return;
      }
      this.orders = await request("/orders/me", "GET");
    },
    async setStatus(order, status) {
      try {
        await request(`/orders/me/${order.id}`, "PATCH", { status });
        uni.showToast({ title: status === "paid" ? "支付成功" : "已取消", icon: "none" });
        this.load();
      } catch (e) {
        uni.showToast({ title: (e && e.detail) || "操作失败", icon: "none" });
      }
    },
    logout() {
      uni.removeStorageSync("token");
      uni.navigateTo({ url: "/pages/login/login" });
    },
  },
};
</script>

<style>
.page { padding: 16px; }
.top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #666;
}
.logout { color: #c0392b; }
.card { background: #fff; padding: 14px; border-radius: 12px; margin-bottom: 10px; }
.row { display: flex; justify-content: space-between; margin-bottom: 8px; }
.remark { color: #888; font-size: 13px; margin-top: 6px; }
.price { color: #c0392b; margin-top: 8px; }
.actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 10px; }
.empty { text-align: center; color: #888; margin-top: 40px; }
</style>
