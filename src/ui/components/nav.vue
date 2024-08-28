<script setup>
</script>

<template>
<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
    <router-link class="navbar-item" to="/">scaffolding</router-link>

    <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>

  <div id="navbarBasicExample" class="navbar-menu">
    <div class="navbar-start">
    <router-link class="navbar-item" to="/samples">Samples</router-link>
    </div>


    <div class="navbar-end">
        <div class="navbar-item">
        <div class="buttons">
          <router-link class="button is-primary" to="/user/register"><strong>Sign up</strong></router-link>
          <router-link class="button is-light" to="/user/login">Log in</router-link>
        </div>
      </div>
    </div>
  </div>
</nav>

</template>
