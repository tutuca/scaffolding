import { createRouter, createWebHistory } from "vue-router";

import { ROUTES } from "/pages";

const aggregatedRoutes = () => {
  return [].concat(...ROUTES);
};

const router = createRouter({
  history: createWebHistory(),
  linkActiveClass: "active",
  linkExactActiveClass: "active",
  routes: aggregatedRoutes(),
});

export default router;
