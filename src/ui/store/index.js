import { reactive, watch } from "vue";
import { useStorage } from "@vueuse/core";

const defaultState = {
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
const state = reactive(defaultState);
const localState = useStorage("application-local-storage", {
  state: defaultState,
});

watch(state, (oldValue, newValue) => {
  localState.state = newValue;
});

export default state;
