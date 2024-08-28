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
        <p class="mt-4">
          {{ item.description }}
        </p>
      </div>
    </div>
    <div class="card-footer">
      <div class="content">
        <slot>
          <p class="card-footer-item"><span class="tag is-primary">{{ item.sample_type }}</span></p>
        </slot>
      </div>
    </div>
  </article>
</template>
