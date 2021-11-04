import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'App',
    component: () => import('src/App.vue'),
  },
  {
    path: '/app',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    children: [
      {
        path: 'list/:type',
        props: true,
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
      {
        path: 'myadvs',
        name: 'MyAdvs',
        component: () => import('../views/property/ManageAdvertisements.vue'),
      },
      {
        path: 'broker',
        name: 'BrokerSetup',
        component: () => import('../views/property/BrokerSetup.vue'),
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
