import state from "/store";
import Profile from "/models/profile.js";

export const main = () => {
  Profile.objects.many().then((response) => {
    state.queryset = response;
  });
  return state;
};

export const detail = (id) => {
  Profile.objects.one(id).then((response) => {
    state.current = response;
  });
  return state;
};
