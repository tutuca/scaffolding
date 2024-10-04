
<script setup>

import { detail } from "./controller"

const props = defineProps(['id']);

const state = detail(props.id);

</script>

<template>
    <div class="container p-4">
        <h1 class="text-lg p-2">Sample {{ state.current.id }}</h1>

    </div>
</template>
