import { defineStore } from "pinia";

const STORE_NAME = "state";
const DEFAULT_STATE = {
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

export const useStore = defineStore(STORE_NAME, {
    state: () => {
        return DEFAULT_STATE;
    },
    persist: {
        storage: sessionStorage,
    },
});
export default useStore;
