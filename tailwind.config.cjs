module.exports = {
  content: [
    "./src/**/*.{html,vue,js,ts}",
    './node_modules/@vueform/vueform/themes/tailwind/**/*.vue',
    './node_modules/@vueform/vueform/themes/tailwind/**/*.js',
  ],
  plugins: [
    require("@tailwindcss/typography"),
    require("daisyui"),
    require('@tailwindcss/forms'),
    require('@vueform/vueform/tailwind'),
  ],
  build: { ssr: true },
  theme: {
    container: {
      center: true,
    },
  },
  daisyui: {
    themes: ["light", "dark"],
  },
};
