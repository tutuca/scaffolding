<script setup>
import { RouterView } from 'vue-router'
import Nav from './components/nav.vue';
</script>

<template>
  <div class="container is-widescreen">
    <Nav />
  </div>
  <div class="container is-widescreen" id="main-content">
    <RouterView />
  </div>
</template>
