<script setup>
import useStore from "/store";
const state = useStore();

</script>
<template>
    <details class="dropdown">
        <template v-if="state.session">
            <summary class="mx-1">{{ state.session.user.username }}</summary>
            <ul class="menu dropdown-content rounded-box z-[1] p-2 shadow">
                <li>
                    <router-link class="button text-nowrap text-blue" to="/profile">
                        <strong>Profile</strong>
                    </router-link>
                </li>
                <li>
                    <router-link class="button text-nowrap text-blue" to="/user/logout">
                        Log out
                    </router-link>
                </li>
            </ul>
        </template>
        <template v-else>
            <summary class="mx-1">Users</summary>
            <ul class="menu dropdown-content text-blue rounded-box z-[1] p-2 shadow">
                <li>
                    <router-link class="button text-nowrap text-blue" to="/user/register">
                        <strong>Sign up</strong>
                    </router-link>
                </li>
                <li>
                    <router-link class="button text-nowrap text-blue" to="/user/login">
                        Log in
                    </router-link>
                </li>
            </ul>
        </template>
    </details>
</template>
