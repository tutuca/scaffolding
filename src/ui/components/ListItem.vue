<script setup>
const props = defineProps(['item'])
</script>
<template>
  <article class="card bg-base-100 w-96 shadow-xl">
  <figure>
    <img
      src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp"
      alt="Shoes" />
  </figure>
  <div class="card-body">
    <h2 class="card-title">{{ item.title }}</h2>
    <p>{{ item.description }}</p>
    <div class="card-actions justify-end">
      <router-link :to="item.url" class="btn btn-primary">more</router-link>
    </div>
  </div>
</article>
</template>
