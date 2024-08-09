<script setup>
const props = defineProps(['item'])

</script>
<template>
  <article class="card">
    <div class="card-content">
      <div class="content">
        <h4>{{ item.title }}</h4>
        <div class="media">
          <div class="media-right">
          </div>
        </div>
        <br />
        <p class="mt-4">
          {{ item.description }}
        </p>
      </div>
    </div>
  </article>
</template>
