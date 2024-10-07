import { defineStore } from "pinia";

const STORE_NAME = "state";

export const useStore = defineStore(
  STORE_NAME,
  {
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
  },
  {
    persist: true,
  },
);

export default useStore;
