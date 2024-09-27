<script setup>
import { ref } from 'vue'
import { main, login } from "./controller"
import LoginForm from "/forms/login/form.vue";
const data = ref({})
const state = main();

</script>

<template>
  <div class="content">
    <LoginForm @submit="login"/>
  </div>
</template>
