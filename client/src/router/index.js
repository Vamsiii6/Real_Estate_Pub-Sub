import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/app',
    name: 'Home',
    component: Home,
    children: [
      {
        path: 'list',
        name: 'PropertyList',
        component: () => import('../views/property/PropertyList.vue'),
      },
      {
        path: 'newproperty',
        name: 'PropertyForm',
        component: () => import('../views/property/PropertyForm.vue'),
      },
      {
        path: 'mysubs',
        name: 'MySubs',
        component: () => import('../views/property/MySubscriptions.vue'),
      },
    ],
  },
  {
    path: '/signup',
    name: 'SignUpPage',
    component: () => import('../views/auth/SignUpPage.vue'),
  },
  {
    path: '/login',
    name: 'LoginPage',
    component: () => import('../views/auth/SignInPage.vue'),
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
})

export default router
