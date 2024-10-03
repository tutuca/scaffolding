module.exports = {
  content: ["./src/**/*.{html,vue,js,ts}"],
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  build: {ssr: true},
  theme: {
    container: {
      center: true,
    },
  },
  daisyui: {
    themes: ["light", "dark"],
  },
};
