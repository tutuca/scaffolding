import Page from "./page.vue";
import ListView from "./list.vue";
import DetailView from "./detail.vue";

// very gusta anonymous export default :)
export default [
  {
    path: "/samples",

    component: Page,
    children: [
      {
        path: "",
        name: "samplesList",
        component: ListView,
      },
      {
        path: ":id",
        name: "samplesDetail",
        component: DetailView,
        props: true,
      },
    ],
  },
];
