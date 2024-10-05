import UserView from "/pages/user/page.vue";
import LoginView from "/pages/user/login.vue";
import LogoutView from "/pages/user/logout.vue";
import RegisterView from "/pages/user/register.vue";

export default [
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
];
