<script setup>

import { RouterView } from 'vue-router'


</script>

<template>
 <div class="container p-4">
    <h1 class="text-lg p-2">User</h1>
    <div class="grid gap-4 grid-flow-col auto-cols-max">
      <RouterView/>
    </div>
  </div>
</template>
