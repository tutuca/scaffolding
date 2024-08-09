import { createApp } from "vue";
import router from "./router";

function initApp(component, selector) {
  const app = createApp(component);
  app.use(router);
  app.mount(selector);
  return app;
}

export default initApp;
