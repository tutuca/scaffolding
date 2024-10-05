import ProfileView from "/pages/profile/page.vue";
import ProfileDetailView from "/pages/profile/detail.vue";

export default [
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
];
