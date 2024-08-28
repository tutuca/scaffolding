<script setup>

import { main } from "./controller"
import List from "/components/List.vue";

const state = main();

</script>

<template>
  <div class="content">
    <h1 class="title">Samples</h1>
    <list :queryset="state.queryset" />
  </div>
</template>
