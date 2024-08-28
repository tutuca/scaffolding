<script setup>
import ListItem from "./ListItem.vue";

const props = defineProps(['queryset'])

</script>

<template>
  <div class="grid">
    <div class="cell" v-for="item in queryset" :key="item.id">
      <ListItem :item="item" />
    </div>
  </div>
</template>
