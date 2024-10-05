<script setup>
import { RouterView } from 'vue-router'
import Nav from './components/Nav.vue';
</script>

<template>
    <div class="container">
        <Nav />
    </div>
    <div class="container grow my-4" id="main-content">
        <RouterView />
    </div>
</template>
