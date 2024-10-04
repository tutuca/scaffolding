import state from "/store";
import Profile from "/models/profile";
import { onBeforeMount } from "vue";

export const main = () => {
  onBeforeMount(() => {
    // TODO: get profile from session
    Profile.objects.many().then((response) => {
      state.queryset = response;
    });
  });
  return state;
};
