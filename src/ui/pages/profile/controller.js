import state from "/store";
import Profile from "/models/profile";
import { onBeforeMount } from "vue";

export const main = () => {
  onBeforeMount(() => {
    Profile.objects.many().then((response) => {
      state.queryset = response;
    });
  });
  return state;
};
