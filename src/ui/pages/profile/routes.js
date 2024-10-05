import Page from "/pages/profile/page.vue";
import DetailView from "/pages/profile/detail.vue";

export default [
  {
    path: "/profile",
    name: "profile",
    component: Page,
    children: [
      {
        path: "/profiles/:id",
        name: "profileDetail",
        component: DetailView,
      },
    ],
  },
];
