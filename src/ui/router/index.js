import { createRouter, createWebHistory } from "vue-router";
import MainView from "/pages/main/page.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: MainView,
    },
  ],
});

export default router;
