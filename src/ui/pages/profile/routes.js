import Page from "/pages/profile/page.vue";
import DetailView from "/pages/profile/detail.vue";

export default [
    {
        path: "/profile",
        name: "profile",
        component: Page,
        children: [
            {
                path: ":id",
                name: "profileDetail",
                component: DetailView,
                props: true,
            },
        ],
    },
];
