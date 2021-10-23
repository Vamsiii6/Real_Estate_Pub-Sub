<template>
  <div
    class="login-page flex w-full flex-col items-center justify-center login-bg"
  >
    <div class="w-6/12 login-container">
      <div class="title-bold">Signup</div>
      <div class="mt-5">
        Name
        <el-input v-model="userModel.displayName"></el-input>
      </div>
      <div class="mt-5">
        Email
        <el-input v-model="userModel.email"></el-input>
      </div>
      <div class="mt-5">
        Phone
        <el-input v-model="userModel.phone"></el-input>
      </div>
      <div class="mt-5">
        Password
        <el-input v-model="userModel.password" show-password></el-input>
      </div>
      <div class="mt-5">
        Roles
        <el-checkbox-group v-model="userModel.roles" class="mt-3">
          <el-checkbox label="Publisher"></el-checkbox>
          <el-checkbox label="Subscriber"></el-checkbox>
        </el-checkbox-group>
      </div>
      <div class="flex items-center flex-col mt-10">
        <el-button class="login-button" @click="signupUserWithFirebase"
          >Sign-up</el-button
        >
        <div class="signup-text mt-5" @click="redirectToSigninPage">
          Already have a account
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { auth } from 'src/plugins/firebase'
export default {
  data: () => ({
    userModel: {
      displayName: null,
      email: null,
      phone: null,
      password: null,
      roles: [],
    },
  }),
  created() {
    if (this.$cookie.get('authToken')) {
      this.redirectToHomePage()
    }
  },
  methods: {
    async signupUserWithFirebase() {
      try {
        let response = await auth.createUserWithEmailAndPassword(
          this.userModel.email,
          this.userModel.password
        )
        if (response.user) {
          let rolesSum = 0
          for (let index in this.userModel.roles) {
            if (this.userModel.roles[index] == 'Publisher') {
              rolesSum += 2
            }
            if (this.userModel.roles[index] == 'Subscriber') {
              rolesSum += 4
            }
          }
          let { user = {} } = response
          let { email, uid } = user || {}
          this.addUserEntryToDb({
            name: this.userModel.displayName,
            email,
            uid,
            phone: this.userModel.displayName,
            roles: rolesSum,
          })
        }
      } catch (error) {
        let { message } = error || {}
        console.log(error)
        this.$message.error(message || 'Signup Failed')
      }
    },
    redirectToLoginPage() {
      this.$router.push({ name: 'LoginPage' })
    },
    async addUserEntryToDb(user) {
      try {
        let response = await this.$axios.post(
          'http://localhost:5000/api/addNewUser',
          {
            userDetails: user,
          }
        )
        if (response) {
          this.redirectToLoginPage()
        }
      } catch (error) {
        this.$message.error(error)
      }
    },

    redirectToHomePage() {
      this.$router.push({ name: 'PropertyList', params: { type: 'all' } })
    },
    redirectToSigninPage() {
      this.$router.push({ name: 'LoginPage' })
    },
  },
}
</script>
