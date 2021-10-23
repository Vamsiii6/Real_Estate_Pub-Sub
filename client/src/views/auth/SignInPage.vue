<template>
  <div
    class="login-page w-full flex flex-col items-center justify-center login-bg"
  >
    <div class="w-6/12 login-container">
      <div class="title-bold">Login</div>
      <div class="mt-5">Email<el-input v-model="email"></el-input></div>
      <div class="mt-5">
        Password<el-input v-model="password" show-password></el-input>
      </div>
      <div class="flex items-center flex-col mt-10">
        <el-button @click="signInUserWithGoogle" class="login-button"
          >Sign-in</el-button
        >
        <div class="signup-text mt-5" @click="redirectToSignupPage">
          Sign-up
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { auth } from 'src/plugins/firebase'
export default {
  data: () => ({
    email: null,
    password: null,
  }),
  created() {
    if (this.$cookie.get('authToken')) {
      this.redirectToHome()
    }
  },
  methods: {
    async signInUserWithGoogle() {
      try {
        let authResponse = await auth.signInWithEmailAndPassword(
          this.email,
          this.password
        )
        try {
          let tkn = await authResponse.user.getIdToken()
          this.$cookie.set('authToken', tkn)
          this.redirectToHome()
        } catch (error) {
          this.$message.error(error)
        }
      } catch (error) {
        if (error) {
          let { message } = error
          this.$message.error(
            message || 'Error on Signin with email and password'
          )
        }
      }
    },
    redirectToSignupPage() {
      this.$router.push({ name: 'SignUpPage' })
    },
    redirectToHome() {
      this.$router.push({ name: 'PropertyList', params: { type: 'all' } })
    },
  },
}
</script>
