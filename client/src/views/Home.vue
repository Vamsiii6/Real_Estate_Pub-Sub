<template>
  <div class="h-screen flex flex-col">
    <div
      class="
        flex flex-row
        items-center
        justify-between
        property-management-home
        bg-blue-500
        h-1/6
        p-5
      "
    >
      <div class="flex flex-row">
        <div
          :class="[
            'hyper-link-1 items-center pr-5',
            $route.name === 'PropertyList' && 'is-active',
          ]"
          @click="routeToList()"
        >
          List
        </div>
        <div
          :class="[
            'hyper-link-1 pr-5',
            $route.name === 'PropertyForm' && 'is-active',
          ]"
          @click="routeToForm()"
        >
          Form
        </div>
      </div>
      <div>
        <el-button
          type="danger"
          icon="el-icon-switch-button"
          circle
          @click="logout()"
        ></el-button>
      </div>
    </div>
    <div class="h-5/6 bg-blue-50 p-10 overflow-y-scroll">
      <router-view />
    </div>
  </div>
</template>

<script>
import helper from 'src/mixins/helper'
export default {
  name: 'Home',
  created() {
    if (!this.$cookie.get('authToken')) {
      this.$router.push({ name: 'LoginPage' })
    }
  },
  methods: {
    routeToList() {
      this.$router.push({ name: 'PropertyList' })
    },
    routeToForm() {
      this.$router.push({ name: 'PropertyForm' })
    },
    logout() {
      helper.reFetchToken()
    },
  },
}
</script>
