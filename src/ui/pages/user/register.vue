<script setup>

import { main } from "./controller"
import RegisterForm from "/components/forms/register/form.vue";

const state = main();

</script>

<template>
  <div class="content">
    <RegisterForm />
  </div>
</template>
