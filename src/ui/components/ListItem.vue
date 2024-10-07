<script setup>
const props = defineProps(["item"]);
</script>
<template>
    <article class="card bg-base-100 w-90 shadow-xl" v-if="item">
        <div class="card-body">
            <h2 class="card-title">{{ item.title }}</h2>
            <p>{{ item.description }}</p>
            <div class="card-actions justify-end">
                <slot name="links" v-if="item.route">
                    <router-link
                        v-if="item.id"
                        :to="item.route"
                        class="btn btn-primary">more</router-link
                    >
                </slot>
            </div>
        </div>
    </article>
</template>
