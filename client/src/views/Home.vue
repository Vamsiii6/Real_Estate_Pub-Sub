<template>
  <div class="h-screen flex flex-col">
    <div
      class="
        flex flex-row
        items-center
        justify-between
        property-management-home
        header-bg
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
              iconClass="icon size-sm"
              class="h-2 w-2"
            />
          </el-button>
          <el-dropdown-menu slot="dropdown" class="drop-menu-re">
            <el-dropdown-item disabled command="my-sub" class="info-part"
              ><i class="el-icon-user"></i> Signed in as
              <span class="font-bold">{{
                `${userDetails.name}`
              }}</span></el-dropdown-item
            >
            <el-dropdown-item
              :divided="(Number(userDetails.roles) & 4) == 4"
              command="my-sub"
              v-if="Number(userDetails.roles) & 4"
              ><i class="el-icon-set-up"></i> Manage
              Subscriptions</el-dropdown-item
            >
            <el-dropdown-item
              :divided="Number(userDetails.roles) == 2"
              command="my-adv"
              v-if="Number(userDetails.roles) & 2"
              ><i class="el-icon-postcard"></i> Manage
              Advertisements</el-dropdown-item
            >
            <el-dropdown-item
              command="syncData"
              v-if="userDetails.uid == 'VwioudRBkCZFvEyNXmNKK7qHZpy1'"
              ><i class="el-icon-refresh"></i> Sync Data from
              API</el-dropdown-item
            >
            <el-dropdown-item
              command="brokerSetup"
              v-if="userDetails.uid == 'VwioudRBkCZFvEyNXmNKK7qHZpy1'"
              ><i class="el-icon-setting"></i> Setup Kafka Broker
              Topics</el-dropdown-item
            >
            <el-dropdown-item command="logout"
              ><i class="el-icon-circle-close"></i> Logout</el-dropdown-item
            >
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
    <div class="h-sub-container p-10 overflow-y-scroll">
      <router-view :key="getType" v-if="!loading && remountFlag" />
      <div v-if="loading">
        <el-skeleton :rows="6" animated></el-skeleton>
      </div>
    </div>
  </div>
</template>

<script>
import helper from 'src/mixins/helper'
import io from 'socket.io-client'
import { mapState } from 'vuex'
export default {
  name: 'Home',
  data: () => ({
    loading: true,
    remountFlag: true,
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
    Promise.resolve(this.fetchUser()).then(() => {
      const socket = io('http://localhost:5002/')
      if (this.userDetails?.uid) {
        socket.on(`socket-${this.userDetails?.uid}`, (...args) => {
          console.log(args)
          let message = ``
          let title = ``
          if (this.$_.get(args, '[0].mode') == 'bulk') {
            title = 'New Listing(s)'
            message = `<b>${this.$_.get(
              args,
              '[0].publisher'
            )}</b> has added few listings for your topics`
            // let partition = this.$_.get(args, '[0].partition')
            // if (!this.$_.isEmpty(partition)) {
            //   message += `<br>Partition: <b>${partition}</b>`
            // }
          } else {
            title = 'New Listing'
            message = `Property <b>${this.$_.get(
              args,
              '[0].property.name'
            )}</b> was added by <b>${this.$_.get(args, '[0].publisher')}</b>`
            message += `<br><br>For topic:`
            let city = this.$_.get(args, '[0].topic_meta.city')
            let room_type = this.$_.get(args, '[0].topic_meta.room_type')
            let partition = this.$_.get(args, '[0].partition')
            if (!this.$_.isEmpty(city)) {
              message += `<br>City: <b>${city}</b>`
            }
            if (!this.$_.isEmpty(room_type)) {
              message += `<br>Room Type: <b>${room_type}</b>`
            }
            if (!this.$_.isEmpty(String(partition))) {
              message += `<br>Partition: <b>${partition}</b>`
            }
          }
          this.$notify.info({
            title: title,
            dangerouslyUseHTMLString: true,
            message,
            duration: 0,
          })
          this.remountFlag = false
          this.$nextTick(() => {
            this.remountFlag = true
          })
        })
      }
    })
    document.title = 'Real Estate Pub Sub'
  },
  beforeUnmount() {
    io('http://localhost:5002/').off(`socket-${this.userDetails?.uid}`)
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
    routeToMyAdvs() {
      this.$router.push({ name: 'MyAdvs' })
    },
    async routeToBrokerSetup() {
      try {
        await this.$axios.get(`http://localhost:5002/api/initializeKafka`)
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
    handleDropDownCommand(command) {
      if (command == 'logout') {
        helper.authLogout()
      } else if (command == 'my-sub') {
        this.routeToMySubs()
      } else if (command == 'my-adv') {
        this.routeToMyAdvs()
      } else if (command == 'syncData') {
        this.fetchDatafromAPI()
      } else if (command == 'brokerSetup') {
        this.routeToBrokerSetup()
      }
    },
    async fetchDatafromAPI() {
      try {
        this.loading = true
        let response = await this.$axios.get(
          `http://localhost:${this.$store.state.port}/api/triggerRapidApi`
        )
        if (response) {
          this.$message.success('Data synced from API successfully')
          this.remountFlag = false
          this.loading = false
          this.$nextTick(() => {
            this.remountFlag = true
          })
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
    async fetchUser() {
      try {
        let response = await this.$axios.get(
          `http://localhost:${this.$store.state.port}/api/getUserDetail`
        )
        if (response?.data?.userDetails) {
          this.$store.commit('setUser', response?.data?.userDetails || {})
          this.loading = false
        }
      } catch (error) {
        this.$message.info('Kindly login to proceed')
      }
    },
  },
}
</script>
