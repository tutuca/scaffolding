<script setup>
import { login } from "./controller";
import LoginForm from "/components/forms/login/form.vue";
</script>

<template>
    <article class="container mx-auto rounded-md shadow-xl p-4">
        <LoginForm @submit="login" />
    </article>
</template>
