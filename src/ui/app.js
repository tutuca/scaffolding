import { createApp } from "vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import router from "./router";
import Vueform from "@vueform/vueform";
import vueformConfig from "./vueform.config";

function initApp(component, selector) {
  const app = createApp(component);
  const pinia = createPinia();
  pinia.use(piniaPluginPersistedstate);
  app.use(pinia);
  app.use(router);

  app.use(Vueform, vueformConfig);
  app.mount(selector);
  return app;
}

export default initApp;
