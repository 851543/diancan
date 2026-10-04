<template>
  <view class="page">
    <view v-if="!items.length" class="empty">购物车是空的</view>
    <view v-for="i in items" :key="i.dish_id" class="card">
      <view>{{ i.name }} × {{ i.qty }}</view>
      <view class="row">
        <text>¥ {{ yuan(i.price_cents * i.qty) }}</text>
        <view>
          <button size="mini" @click="change(i.dish_id, -1)">-</button>
          <button size="mini" @click="change(i.dish_id, 1)">+</button>
        </view>
      </view>
    </view>
    <view class="bar" v-if="items.length">
      <text>合计 ¥ {{ yuan(total) }}</text>
      <button type="primary" @click="submit">下单</button>
    </view>
  </view>
</template>

<script>
import { request } from "../../utils/api";
import { addCartItem, fetchCart } from "../../utils/cart";
import { cartTotal, yuan } from "../../utils/price";

export default {
  data() {
    return { items: [] };
  },
  computed: {
    total() {
      return cartTotal(this.items);
    },
  },
  onShow() {
    this.load();
  },
  methods: {
    yuan,
    async load() {
      if (!uni.getStorageSync("token")) {
        uni.navigateTo({ url: "/pages/login/login" });
        return;
      }
      try {
        const data = await fetchCart();
        this.items = (data && data.items) || [];
      } catch (e) {
        this.items = [];
        uni.showToast({ title: (e && e.detail) || "购物车加载失败", icon: "none" });
      }
    },
    async change(id, delta) {
      try {
        const data = await addCartItem(id, delta);
        this.items = (data && data.items) || [];
      } catch (e) {
        uni.showToast({ title: (e && e.detail) || "修改失败", icon: "none" });
      }
    },
    async submit() {
      try {
        await request("/orders", "POST", {
          items: this.items.map((i) => ({ dish_id: i.dish_id, qty: i.qty })),
          remark: "",
        });
        this.items = [];
        uni.showToast({ title: "下单成功" });
        uni.switchTab({ url: "/pages/orders/orders" });
      } catch (e) {
        uni.showToast({ title: e.detail || "下单失败", icon: "none" });
      }
    },
  },
};
</script>

<style>
.page { padding: 16px 16px 80px; }
.card { background: #fff; padding: 14px; border-radius: 12px; margin-bottom: 10px; }
.row { display: flex; justify-content: space-between; margin-top: 8px; }
.empty { text-align: center; color: #888; margin-top: 40px; }
.bar {
  position: fixed; left: 0; right: 0; bottom: 0;
  background: #fff; padding: 12px 16px;
  display: flex; justify-content: space-between; align-items: center;
}
</style>
