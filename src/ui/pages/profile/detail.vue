
<script setup>
import useStore from "/store";
import { onBeforeMount } from "vue";

import { detail } from "./controller"

const props = defineProps(['id']);
const state = useStore();


onBeforeMount(()=> {
    detail(props.id);
})
</script>

<template>
    <div class="container p-4">
        <h1 class="text-lg p-2" v-if="state.current">Profile {{ state.current.id }}</h1>
        <h1 class="text-lg p-2" v-else>Profile  </h1>
    </div>
</template>
