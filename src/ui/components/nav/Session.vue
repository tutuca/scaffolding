<script setup>
import state from "/store";

</script>
<template>
    <details>
        <template v-if="state.session">
            <summary >{{ state.session.username }}</summary>
            <ul class="p-2">
                <li>
                    <router-link class="button text-nowrap is-primary" to="/profile">
                        <strong>Profile</strong>
                    </router-link>
                </li>
                <li>
                    <router-link class="button text-nowrap is-light" to="/user/logout">
                        Log out
                    </router-link>
                </li>
            </ul>
        </template>
        <template v-else>
        <summary>Users</summary>
        <ul class="p-2">
            <li>
            <router-link class="button text-nowrap is-primary" to="/user/register">
                <strong>Sign up</strong>
                </router-link>
            </li>
            <li>
            <router-link class="button text-nowrap is-light" to="/user/login">
                Log in
            </router-link>
            </li>
        </ul>
        </template>
    </details>
</template>
