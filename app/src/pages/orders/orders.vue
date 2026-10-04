<template>
  <view class="page">
    <view v-for="o in orders" :key="o.id" class="card">
      <view class="row">
        <text>#{{ o.id }}</text>
        <text>{{ statusText(o.status) }}</text>
      </view>
      <view v-for="i in o.items" :key="i.dish_id">{{ i.name }} × {{ i.qty }}</view>
      <view class="price">¥ {{ yuan(o.total_cents) }}</view>
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
  },
};
</script>

<style>
.page { padding: 16px; }
.card { background: #fff; padding: 14px; border-radius: 12px; margin-bottom: 10px; }
.row { display: flex; justify-content: space-between; margin-bottom: 8px; }
.price { color: #c0392b; margin-top: 8px; }
.empty { text-align: center; color: #888; margin-top: 40px; }
</style>
