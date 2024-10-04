<script setup>
import { ref } from 'vue'
import { main, login } from "./controller"
import LoginForm from "/components/forms/login/form.vue";
const data = ref({})
const state = main();

</script>

<template>
  <article class="container mx-auto rounded-md shadow-xl p-4">
      <LoginForm @submit="login"/>
  </article>
</template>
