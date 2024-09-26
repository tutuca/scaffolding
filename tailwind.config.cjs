module.exports = {
  content: ["./src/**/*.{vue,js,ts}"],
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  theme: {
    container: {
      center: true,
    },
  },
  daisyui: {
    themes: ["light", "dark"],
  },
};
