<template>
  <div class="h-screen flex flex-col">
    <div
      class="
        flex flex-row
        items-center
        justify-between
        property-management-home
        header-bg
        h-20
        p-5
      "
    >
      <div class="flex flex-row">
        <div
          :class="[
            'hyper-link-1 items-center hover-effect',
            $route.name === 'PropertyList' && 'is-active',
          ]"
          @click="routeToList()"
        >
          My Properties
        </div>
        <div class="hyper-link-1 pr-5 pl-5">|</div>
        <div
          :class="[
            'hyper-link-1',
            $route.name === 'PropertyForm' && 'is-active',
          ]"
          @click="routeToForm()"
        >
          Subscribed Properties
        </div>
        <div class="hyper-link-1 pr-5 pl-5">|</div>
        <div
          :class="[
            'hyper-link-1 pr-5',
            $route.name === 'PropertyForm' && 'is-active',
          ]"
          @click="routeToForm()"
        >
          All Properties
        </div>
      </div>
      <div>
        <el-dropdown trigger="click" @command="handleDropDownCommand">
          <el-button circle type="primary">
            <InlineSvg
              src="settings"
              iconClass="icon size-100"
              class="h-10 w-10"
            />
          </el-button>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="my-sub"
              >My Subscriptions</el-dropdown-item
            >
            <el-dropdown-item command="logout">Logout</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
    <div class="h-5/6 bg-blue-50 p-10 overflow-y-scroll">
      <router-view />
    </div>
  </div>
</template>

<script>
import helper from 'src/mixins/helper'
import io from 'socket.io-client'

export default {
  name: 'Home',
  created() {
    if (this.$cookie && !this.$cookie.get('authToken')) {
      this.$router.push({ name: 'LoginPage' })
    }
    const socket = io('http://localhost:5000/')
    socket.on('testing-event', (...args) => {
      console.log('Inside event', args)
    })
  },
  methods: {
    routeToList() {
      this.$router.push({ name: 'PropertyList' })
    },
    routeToForm() {
      this.$router.push({ name: 'PropertyForm' })
    },
    routeToMySubs() {
      this.$router.push({ name: 'MySubs' })
    },
    handleDropDownCommand(command) {
      if (command == 'logout') {
        helper.authLogout()
      } else if (command == 'my-sub') {
        this.routeToMySubs()
      }
    },
  },
}
</script>
