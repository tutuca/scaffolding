import { createRouter, createWebHistory } from "vue-router";
import MainView from "/pages/main/page.vue";
import UserView from "/pages/user/page.vue";
import LoginView from "/pages/user/login.vue";
import LogoutView from "/pages/user/logout.vue";
import RegisterView from "/pages/user/register.vue";
import ProfileView from "/pages/profile/page.vue";
import ProfileDetailView from "/pages/profile/detail.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: MainView,
    },
    {
      path: "/samples",
      name: "samples",
      component: MainView,
      children: [
        {
          path: "samples/:id",
          name: "samplesDetail",
          component: LoginView,
        },
      ],
    },
    {
      path: "/profile",
      name: "profile",
      component: ProfileView,
      children: [
        {
          path: "/profiles/:id",
          name: "profileDetail",
          component: ProfileDetailView,
        },
      ],
    },
    {
      path: "/user/",
      component: UserView,
      children: [
        {
          path: "login",
          component: LoginView,
        },
        {
          path: "logout",
          component: LogoutView,
        },

        {
          path: "register",
          component: RegisterView,
        },
      ],
    },
  ],
});

export default router;
