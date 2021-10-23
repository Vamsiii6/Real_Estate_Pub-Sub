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
      <div v-if="loading"></div>
      <div v-else class="flex flex-row">
        <div
          :class="[
            'hyper-link-1 items-center hover-effect',
            getType === 'myown' && 'is-active',
          ]"
          v-if="Number(userDetails.roles) & 2"
          @click="routeToList('myown')"
        >
          My Properties
        </div>
        <div
          v-if="Number(userDetails.roles) & 2"
          class="hyper-link-1 pr-5 pl-5"
        >
          |
        </div>
        <div
          :class="[
            'hyper-link-1 hover-effect',
            getType === 'subscribed' && 'is-active',
          ]"
          v-if="Number(userDetails.roles) & 4"
          @click="routeToList('subscribed')"
        >
          Subscribed Properties
        </div>
        <div
          v-if="Number(userDetails.roles) & 4"
          class="hyper-link-1 pr-5 pl-5"
        >
          |
        </div>
        <div
          :class="[
            'hyper-link-1 pr-5 hover-effect',
            getType === 'all' && 'is-active',
          ]"
          @click="routeToList('all')"
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
              ><i class="el-icon-set-up"></i> My Subscriptions</el-dropdown-item
            >
            <el-dropdown-item command="syncData"
              ><i class="el-icon-refresh"></i> Sync Data from
              API</el-dropdown-item
            >
            <el-dropdown-item command="logout"
              ><i class="el-icon-circle-close"></i> Logout</el-dropdown-item
            >
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
    <div class="h-sub-container bg-white p-10 overflow-y-scroll">
      <router-view :key="getType" v-if="!loading" />
      <div v-if="loading">
        <el-skeleton :rows="6" animated></el-skeleton>
      </div>
    </div>
  </div>
</template>

<script>
import helper from 'src/mixins/helper'
// import io from 'socket.io-client'
import { mapState } from 'vuex'

export default {
  name: 'Home',
  data: () => ({
    loading: true,
  }),
  computed: {
    ...mapState({ userDetails: (state) => state.userDetails }),
    getType() {
      return this.$route?.params?.type || ''
    },
  },
  created() {
    if (this.$cookie && !this.$cookie.get('authToken')) {
      this.$router.push({ name: 'LoginPage' })
    }
    this.fetchUser()
    // const socket = io('http://localhost:5000/')
    // socket.on('testing-event', (...args) => {
    //   console.log('Inside event', args)
    // })
  },
  methods: {
    routeToList(type) {
      this.$router.push({ name: 'PropertyList', params: { type } })
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
    async fetchUser() {
      try {
        let response = await this.$axios.get('/getUserDetail')
        if (response?.data?.userDetails) {
          this.$store.commit('setUser', response?.data?.userDetails || {})
          this.loading = false
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
  },
}
</script>
