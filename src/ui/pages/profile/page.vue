<script setup>
import { main } from "./controller";

const state = main();
</script>

<template>
    <div class="container p-4">
        <h1 class="text-lg p-2">{{ state.session.username }}</h1>
        <div class="grid gap-4 grid-flow-col auto-cols-max">
            <RouterView />
        </div>
    </div>
</template>
