<script setup>
import ListItem from "./ListItem.vue";

const props = defineProps(['queryset'])

</script>

<template>
  <div class="grid gap-4 grid-flow-col auto-cols-max">
    <template v-for="item in queryset" :key="item.id">
      <ListItem :item="item" />
    </template>
  </div>
</template>
