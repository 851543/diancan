import { createRouter, createWebHistory } from "vue-router";
import Login from "./views/Login.vue";
import Layout from "./views/Layout.vue";
import Dishes from "./views/Dishes.vue";
import Orders from "./views/Orders.vue";
import Dashboard from "./views/Dashboard.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: Login },
    {
      path: "/",
      component: Layout,
      children: [
        { path: "", component: Dashboard },
        { path: "dishes", component: Dishes },
        { path: "orders", component: Orders },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (to.path !== "/login" && !token) return "/login";
});

export default router;
