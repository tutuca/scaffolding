<template>
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
            <li>
                <router-link class="navbar-item" to="/samples"
                    >Samples</router-link
                >
            </li>
            <li>
                <a>Profile</a>
                <ul class="p-2">
                    <li>
                        <router-link
                            class="button is-primary"
                            to="/user/register"
                            ><strong>Sign up</strong></router-link
                        >
                    </li>
                    <li>
                        <router-link class="button is-light" to="/user/login"
                            >Log in</router-link
                        >
                    </li>
                </ul>
            </li>
        </ul>
    </div>
    <router-link class="btn btn-ghost text-xl" to="/">Scaffolding</router-link>
</template>
