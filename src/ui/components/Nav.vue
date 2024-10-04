<script setup>
import DarkToggle from "./nav/DarkToggle.vue";
import Session from "./nav/Session.vue";
import Burger from "./nav/Burger.vue";
</script>

<template>
    <nav class="navbar bg-base-100">
        <div class="navbar-start">
            <burger />
        </div>
        <div class="navbar-end hidden lg:flex">
            <ul class="menu menu-horizontal px-1 z-50">
                <li>
                    <router-link class="navbar-item" to="/samples">Samples</router-link>
                </li>
                <li>
                    <session />
                </li>
                <li><dark-toggle /></li>
            </ul>
        </div>
    </nav>
</template>
