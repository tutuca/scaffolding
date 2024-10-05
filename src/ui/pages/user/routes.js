import Page from "/pages/user/page.vue";
import Login from "/pages/user/login.vue";
import Logout from "/pages/user/logout.vue";
import Register from "/pages/user/register.vue";

export default [
  {
    path: "/user/",
    component: Page,
    children: [
      {
        path: "login",
        component: Login,
      },
      {
        path: "logout",
        component: Logout,
      },

      {
        path: "register",
        component: Register,
      },
    ],
  },
];
