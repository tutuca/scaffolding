<script setup>
import { RouterView } from 'vue-router'
import Nav from './components/nav.vue';
</script>

<template>
  <div class="container">
    <Nav />
  </div>
  <div class="container" id="main-content">
    <RouterView />
  </div>
</template>
