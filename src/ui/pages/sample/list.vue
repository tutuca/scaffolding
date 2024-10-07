<script setup>
import { main } from "./controller";
import List from "/components/List.vue";

const state = main();
</script>

<template>
    <div class="container p-4">
        <h1 class="text-lg p-2">Samples</h1>
        <list :queryset="state.queryset" />
    </div>
</template>
