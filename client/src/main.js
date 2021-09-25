import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import "./css/index.css";
import "./scss/common.scss";
import Element from "element-ui";
import "element-ui/lib/theme-chalk/index.css";
import _ from "lodash";

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
Vue.use(Element);
Object.defineProperty(Vue.prototype, "$_", { value: _ });
