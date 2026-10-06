<template>
  <div>
    <div class="bar">
      <h3>菜单</h3>
      <div class="filters">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索菜名"
          style="width: 200px"
        />
        <el-select v-model="category" clearable placeholder="分类" style="width: 140px">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-button type="primary" @click="openEdit()">新增菜品</el-button>
      </div>
    </div>
    <el-table :data="filteredRows" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column label="价格" width="120">
        <template #default="{ row }">{{ (row.price_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="上架" width="80">
        <template #default="{ row }">{{ row.is_on ? "是" : "否" }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑' : '新增'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="价格(分)">
          <el-input-number v-model="form.price_cents" :min="1" :step="100" />
        </el-form-item>
        <el-form-item label="图片">
          <el-input v-model="form.image_url" placeholder="图片 URL（选填）" />
        </el-form-item>
        <el-form-item label="上架">
          <el-switch v-model="form.is_on" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api";

const allRows = ref([]);
const keyword = ref("");
const category = ref("");
const visible = ref(false);
const form = reactive({
  id: null,
  name: "",
  category: "热菜",
  description: "",
  price_cents: 1800,
  image_url: "",
  is_on: 1,
});

const categories = computed(() => [
  ...new Set(allRows.value.map((r) => r.category).filter(Boolean)),
]);

const filteredRows = computed(() => {
  const kw = keyword.value.trim();
  return allRows.value.filter((r) => {
    if (kw && !(r.name || "").includes(kw)) return false;
    if (category.value && r.category !== category.value) return false;
    return true;
  });
});

async function load() {
  allRows.value = (await http.get("/dishes/admin")).data;
}

function openEdit(row) {
  if (row) Object.assign(form, row);
  else
    Object.assign(form, {
      id: null,
      name: "",
      category: "热菜",
      description: "",
      price_cents: 1800,
      image_url: "",
      is_on: 1,
    });
  visible.value = true;
}

async function save() {
  const payload = {
    name: form.name,
    category: form.category,
    description: form.description,
    price_cents: form.price_cents,
    image_url: form.image_url || "",
    is_on: form.is_on,
  };
  if (form.id) await http.put(`/dishes/admin/${form.id}`, payload);
  else await http.post("/dishes/admin", payload);
  ElMessage.success("已保存");
  visible.value = false;
  load();
}

async function remove(row) {
  try {
    await http.delete(`/dishes/admin/${row.id}`);
    ElMessage.success("已删除");
    load();
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || "删除失败");
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
}
.filters {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
