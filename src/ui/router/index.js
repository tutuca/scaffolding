import { createRouter, createWebHistory } from "vue-router";
import MainView from "/pages/main/page.vue";
import UserView from "/pages/user/page.vue";
import LoginView from "/pages/user/login.vue";
import RegisterView from "/pages/user/register.vue";
import ProfileView from "/pages/profile/page.vue";

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
    },
    {
      path: "/user/:id",
      component: UserView,
      children: [
        {
          // UserProfile will be rendered inside User's <router-view>
          // when /user/:id/profile is matched
          path: "profile",
          component: ProfileView,
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
          path: "register",
          component: RegisterView,
        },
      ],
    },
  ],
});

export default router;
