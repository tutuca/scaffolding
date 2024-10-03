import { createApp } from "vue";
import router from "./router";
import Vueform from "@vueform/vueform";
import vueformConfig from "./vueform.config";

function initApp(component, selector) {
  const app = createApp(component);
  app.use(router);
  app.use(Vueform, vueformConfig);
  app.mount(selector);
  return app;
}

export default initApp;
