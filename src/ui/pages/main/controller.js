import state from "/store";
import Sample from "/models/sample";
import { onBeforeMount } from "vue";

export const main = () => {
  onBeforeMount(() => {
    Sample.objects.many().then((response) => {
      state.queryset = response;
    });
  });
  return state;
};
