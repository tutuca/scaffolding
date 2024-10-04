<script setup>

import { main } from "./controller"
import RegisterForm from "/components/forms/register/form.vue";

const state = main();

</script>

<template>
  <article class="container mx-auto rounded-md shadow-xl p-4">
    <RegisterForm />
  </article>
</template>
