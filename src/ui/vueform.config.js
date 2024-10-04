import es from "@vueform/vueform/locales/es";
import tailwind from '@vueform/vueform/dist/tailwind'
import { defineConfig } from "@vueform/vueform";

export default defineConfig({
  theme: tailwind,
  locales: { es },
  locale: "es",
});
