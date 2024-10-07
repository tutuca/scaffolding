import ListView from "/pages/sample/page.vue";
import DetailView from "/pages/sample/detail.vue";

// very gusta anonymous export default :)
export default [
    {
        path: "/samples",
        name: "samples",
        component: ListView,
        children: [
            {
                path: "samples/:id",
                name: "samplesDetail",
                component: DetailView,
            },
        ],
    },
];
