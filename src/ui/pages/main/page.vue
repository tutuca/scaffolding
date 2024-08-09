<script setup>
import store from "@/store";
import Sample from "@/models/sample";
import { onMounted } from "vue";
import List from "@/components/List.vue";

onMounted(() => {
  Sample.objects.many().then(response => {
    store.queryset = response;
  });
});

</script>

<template>
    <div class="content">
    <h1 class="title">Samples</h1>
    <list :queryset="store.queryset"/>
    </div>
</template>
