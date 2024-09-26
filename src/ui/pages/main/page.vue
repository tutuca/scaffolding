<script setup>

import { main } from "./controller"
import List from "/components/List.vue";

const state = main();

</script>

<template>
    <div class="container mx-auto p-4">
        <h1 class="text-lg p-4">Samples</h1>
        <list :queryset="state.queryset" />
    </div>
</template>
