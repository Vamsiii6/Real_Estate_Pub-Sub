import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './css/index.css'
import './scss/common.scss'
import Element from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import _ from 'lodash'
import InlineSvg from './components/InlineSvg'
import VueCookie from 'vue-cookie'
import http from '@/http'
Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app')
Vue.use(Element)
Vue.use(VueCookie)

Vue.component('InlineSvg', InlineSvg)

Object.defineProperty(Vue.prototype, '$_', { value: _ })
Object.defineProperty(Vue.prototype, '$axios', { value: http })
