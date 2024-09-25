<template>
<nav class="navbar bg-base-100">
  <div class="flex-1">
    <a class="btn btn-ghost text-xl">Scaffolding</a>
  </div>
  <div class="flex-none">
    <ul class="menu menu-horizontal px-1">
      <li><router-link class="navbar-item" to="/samples">Samples</router-link></li>
      <li>
        <details>
          <summary>Profile</summary>
          <ul class="bg-base-100 rounded-t-none p-2">
            <li>
              <router-link class="button is-primary" to="/user/register"><strong>Sign up</strong></router-link>
            </li>
            <li>
              <router-link class="button is-light" to="/user/login">Log in</router-link>
            </li>
          </ul>
        </details>
      </li>
    </ul>
  </div>
</nav>
</template>
