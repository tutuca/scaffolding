<script setup>
const navigation = (router) => {
  // TODO: build navigation from router.options.
  // TODO: flag router items to tell if they show in menu.
  return [
    { to: "/samples", label: "Samples" },
    {
      to: "/profile",
      label: "Profile",
      children: [
        { to: "/user/login", label: "Log in" },
        { to: "/user/register", label: "Sign in" },
      ],
    },
  ];
};
</script>

<template>
  <nav class="navbar bg-base-100">
    <div class="navbar-start">
      <div class="dropdown">
        <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h8m-8 6h16"
            />
          </svg>
        </div>

        <ul
          tabindex="0"
          class="menu menu-sm dropdown-content bg-base-100 rounded-box z-50 mt-3 w-52 p-2 shadow"
        >
          <li v-for="item in navigation()" :key="item.label">
            <router-link class="navbar-item" :to="item.to">{{item.label}}</router-link>
            <template v-if="item.children">
              <ul class="p-2">
                <li v-for="child in item.children" :key="child.label">
                  <router-link :to="child.to">{{child.label}}</router-link>
                </li>
              </ul>
            </template>
          </li>
        </ul>
      </div>
      <router-link class="btn btn-ghost text-xl" to="/"
        >Scaffolding</router-link
      >
    </div>
    <div class="navbar-end hidden lg:flex z-50">
      <ul class="menu menu-horizontal px-1">
        <li v-for="item in navigation()" :key="item.label">
          <template v-if="item.children">
            <details>
              <summary>{{ item.label }}</summary>
              <ul class="p-2">
                <li v-for="child in item.children" :key="child.label">
                  <router-link class="navbar-item text-nowrap" :to="child.to">{{child.label}}</router-link>
                </li>
              </ul>
            </details>
          </template>
          <template v-else>
            <router-link class="navbar-item" :to="item.to">{{
              item.label
            }}</router-link>
          </template>
        </li>
      </ul>
    </div>
  </nav>
</template>
