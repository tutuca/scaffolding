import { reactive } from "vue";

export const store = reactive({
  current: null,
  loading: true,
  model: null,
  nextPage: "",
  prevPage: "",
  query: {},
  queryset: [],
});

export default store;
