<template>
  <div class="h-full flex w-full flex-col items-center justify-center">
    <div class="w-6/12">
      <div>Signup as New User</div>
      <div>
        Name
        <el-input v-model="userModel.displayName"></el-input>
      </div>
      <div>
        Email
        <el-input v-model="userModel.email"></el-input>
      </div>
      <div>
        Phone
        <el-input v-model="userModel.phone"></el-input>
      </div>
      <div>
        Password
        <el-input v-model="userModel.password" show-password></el-input>
      </div>
      <div>
        Roles
        <el-checkbox-group v-model="userModel.roles">
          <el-checkbox label="Seller"></el-checkbox>
          <el-checkbox label="Buyer"></el-checkbox>
        </el-checkbox-group>
      </div>
      <div>
        <el-button class="w-20" @click="signupUserWithFirebase"
          >Signup</el-button
        >
      </div>
    </div>
  </div>
</template>
<script>
import http from '@/http'
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
  methods: {
    async signupUserWithFirebase() {
      try {
        let response = await auth.createUserWithEmailAndPassword(
          this.userModel.email,
          this.userModel.password
        )
        if (response.user) {
          let rolesSum = 0
          for (let role in this.userModel.roles) {
            if (role == 'Seller') {
              rolesSum += 2
            }
            if (role == 'Buyer') {
              rolesSum += 4
            }
          }
          let { user = {} } = response
          let { displayName, email, uid, phone } = user || {}
          this.addUserEntryToDb({
            name: displayName,
            email,
            uid,
            phone,
            roles: rolesSum,
          })
          this.redirectToLoginPage()
        }
      } catch (error) {
        let { message } = error || {}
        this.errorMessage = message
      }
    },
    redirectToLoginPage() {
      this.$router.push({ name: 'LoginPage' })
    },
    async addUserEntryToDb(user) {
      try {
        await http.post('/api/user/add', user)
      } catch (error) {
        this.$message.error(error)
      }
    },
  },
}
</script>
