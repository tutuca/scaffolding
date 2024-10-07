import useStore from "/store";
import Profile from "/models/profile.js";

export const main = () => {
    const state = useStore();

    Profile.objects.many().then((response) => {
        state.queryset = response;
    });
    return state;
};

export const detail = (id) => {
    const state = useStore();

    Profile.objects.one(id).then((response) => {
        state.current = response;
    });
    return state;
};
