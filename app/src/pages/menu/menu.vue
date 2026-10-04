<template>
  <view class="page">
    <view class="search">
      <input
        class="search-input"
        v-model="keyword"
        placeholder="搜索菜名"
        confirm-type="search"
        @confirm="load"
        @input="onKeyword"
      />
    </view>
    <scroll-view class="cats" scroll-x>
      <view
        class="cat"
        :class="{ on: category === '' }"
        @click="pickCategory('')"
      >全部</view>
      <view
        v-for="c in categories"
        :key="c"
        class="cat"
        :class="{ on: category === c }"
        @click="pickCategory(c)"
      >{{ c }}</view>
    </scroll-view>
    <view v-if="!dishes.length" class="empty">没有符合条件的菜品</view>
    <view v-for="d in dishes" :key="d.id" class="card">
      <view class="name">{{ d.name }}</view>
      <view class="meta">{{ d.category }} · {{ d.description }}</view>
      <view class="row">
        <text class="price">¥ {{ yuan(d.price_cents) }}</text>
        <button size="mini" type="primary" @click="add(d)">加入</button>
      </view>
    </view>
  </view>
</template>

<script>
import { request } from "../../utils/api";
import { addCartItem } from "../../utils/cart";
import { yuan } from "../../utils/price";

export default {
  data() {
    return {
      dishes: [],
      categories: [],
      keyword: "",
      category: "",
      timer: null,
    };
  },
  onShow() {
    if (!uni.getStorageSync("token")) {
      uni.navigateTo({ url: "/pages/login/login" });
      return;
    }
    this.bootstrap();
  },
  methods: {
    yuan,
    async bootstrap() {
      const all = await request("/dishes", "GET");
      this.categories = [...new Set((all || []).map((d) => d.category).filter(Boolean))];
      await this.load();
    },
    query() {
      const data = {};
      const kw = (this.keyword || "").trim();
      if (kw) data.keyword = kw;
      if (this.category) data.category = this.category;
      return data;
    },
    async load() {
      const data = this.query();
      this.dishes = await request("/dishes", "GET", Object.keys(data).length ? data : undefined);
    },
    onKeyword() {
      clearTimeout(this.timer);
      this.timer = setTimeout(() => this.load(), 300);
    },
    pickCategory(c) {
      this.category = c;
      this.load();
    },
    async add(d) {
      try {
        await addCartItem(d.id, 1);
        uni.showToast({ title: "已加入购物车", icon: "none" });
      } catch (e) {
        uni.showToast({ title: (e && e.detail) || "加入失败", icon: "none" });
      }
    },
  },
};
</script>

<style>
.page { padding: 16px; }
.search { margin-bottom: 10px; }
.search-input {
  background: #fff;
  padding: 10px 12px;
  border-radius: 10px;
}
.cats {
  white-space: nowrap;
  margin-bottom: 12px;
}
.cat {
  display: inline-block;
  padding: 6px 14px;
  margin-right: 8px;
  border-radius: 16px;
  background: #eee;
  font-size: 13px;
}
.cat.on { background: #c0392b; color: #fff; }
.card {
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
}
.name { font-size: 18px; font-weight: 600; }
.meta { color: #888; margin: 6px 0; }
.row { display: flex; justify-content: space-between; align-items: center; }
.price { color: #c0392b; font-size: 18px; }
.empty { text-align: center; color: #888; margin: 40px 0; }
</style>
