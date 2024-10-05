<script setup>

import { detail } from "./controller"

const props = defineProps(['id']);

const state = detail(props.id);

</script>

<template>
    <div class="container p-4">
        <template v-if="state.current">
            <h1 class="text-lg p-2">{{ state.current.title }}</h1>
            <p>{{ state.current.description }}</p>
        </template>
    </div>
</template>
