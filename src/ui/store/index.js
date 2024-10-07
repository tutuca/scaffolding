import { defineStore } from "pinia";

export const useStore = defineStore("state", {
  // arrow function recommended for full type inference
  state: () => {
    return {
      current: null,
      loading: true,
      model: null,
      nextPage: "",
      prevPage: "",
      query: {},
      theme: null,
      session: null,
      queryset: [],
    };
  },
});

export default useStore;
