<template>
  <div class="h-full w-full flex flex-col items-center justify-center">
    <div class="w-6/12">
      <div>Login Page</div>
      <div>Name<el-input v-model="email"></el-input></div>
      <div>Password<el-input v-model="password" show-password></el-input></div>
      <div>
        <el-button @click="signInUserWithGoogle">Sign-in</el-button>
        <el-button @click="redirectToSignupPage">Sign-up</el-button>
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
    loading: true,
  }),
  created() {
    if (this.$cookie.get('authToken')) {
      this.redirectToHomePage()
    } else {
      this.loading = false
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
          this.redirectToHomePage()
        } catch (error) {
          this.$message.error(error)
        }
      } catch (error) {
        if (error) {
          let { message } = error
          console.error(message || 'Error on Signin with email and password')
        }
      }
    },
    redirectToSignupPage() {
      this.$router.push({ name: 'SignUpPage' })
    },
    redirectToHomePage() {
      this.$router.push({ name: 'PropertyList' })
    },
  },
}
</script>
