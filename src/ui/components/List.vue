<script setup>
import ListItem from "./ListItem.vue";

const props = defineProps(["queryset"]);
</script>

<template>
    <div class="grid grid-cols-3 auto-rows-fr gap-4 px-0">
        <template v-for="item in queryset" :key="item.id">
            <ListItem :item="item" />
        </template>
    </div>
</template>
