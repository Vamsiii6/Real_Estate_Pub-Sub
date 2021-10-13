import router from 'src/router'
import Vue from 'vue'
import { auth } from 'src/plugins/firebase'

export default {
  async reFetchToken() {
    await auth.signOut()
    Vue.prototype.$cookie.delete('authToken')
    router.push({ name: 'LoginPage' })
  },
}
