<script setup>
import { logout } from "./controller"
import LogoutForm from "/components/forms/logout/form.vue";

</script>

<template>
  <article class="container mx-auto rounded-md shadow-xl p-4">
      <LogoutForm @submit="logout"/>
  </article>
</template>
