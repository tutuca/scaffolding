<script setup>
import { main } from "./controller"

const state = main();
</script>

<template>
    <section class="pt-20 md:pt-40">
        <div class="container mx-auto px-8 lg:flex">
            <div class="text-center lg:text-left lg:w-1/2">
                <h1 class="text-4xl lg:text-5xl xl:text-6xl font-bold leading-none">Lorem ipsum dolor sit amet</h1>
                <p class="text-xl lg:text-2xl mt-6 font-light">Donec odio dolor, molestie id tincidunt ac, bibendum non arcu. Integer nec convallis dui</p>
                <p class="mt-8 md:mt-12">
                    <button type="button"
                            class="py-4 px-12 bg-teal-500 hover:bg-teal-600 rounded text-white">
                            Get Started
                    </button>
                </p>
                <p class="my-4 text-gray-600">Integer nec convallis dui. Aliquam erat volutpat. Donec scelerisque, nulla ut accumsan tristique, lacus felis imperdiet arcu, a pellentesque magna metus sed lorem. </p>
            </div>

        </div>
    </section>
</template>
