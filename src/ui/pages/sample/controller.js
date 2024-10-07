import { onBeforeMount } from "vue";

import useStore from "/store";
import Sample from "/models/sample";

export const main = () => {
    const state = useStore();
    onBeforeMount(async () => (state.queryset = await Sample.objects.many()));
    return state;
};

export const detail = async (id) => {
    const state = useStore();
    onBeforeMount(async () => (state.current = await Sample.objects.one(id)));
    return state;
};
