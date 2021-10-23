<template>
  <div class="property-form">
    <div class="flex flex-row justify-between w-4/5">
      <div class="heading-1">Create New Property</div>
      <div>
        <el-button @click="saveForm()" type="primary" plain size="medium"
          >Publish</el-button
        >
        <el-button
          type="danger"
          plain
          @click="routeToPropertyList()"
          size="medium"
          >Cancel</el-button
        >
      </div>
    </div>
    <el-form
      label-position="top"
      class="w-4/5"
      :rules="formRules"
      :model="formModel"
      ref="property-form"
    >
      <el-form-item class="mt-10 mb-10 w-full" label="Address" prop="name">
        <el-input v-model="formModel.name" class="w-full"></el-input>
      </el-form-item>
      <el-form-item class="mt-10 mb-10 w-full" label="Price" prop="price">
        <el-input
          type="number"
          v-model="formModel.price"
          class="w-full"
        ></el-input>
      </el-form-item>
      <el-form-item class="mt-10 mb-10 w-full" label="City" prop="city_id">
        <el-select
          v-model="formModel.city_id"
          placeholder="Select City"
          class="w-full"
        >
          <el-option
            v-for="city in allCites"
            :key="city.id"
            :label="city.name"
            :value="city.id"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item
        class="mt-10 mb-10 w-full"
        label="Room Type"
        prop="room_type_id"
      >
        <el-select
          v-model="formModel.room_type_id"
          placeholder="Select Room Type"
          class="w-full"
        >
          <el-option
            v-for="type in allRoomTypes"
            :key="type.id"
            :label="type.type"
            :value="type.id"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item class="mt-10 mb-10" label="Description" prop="description">
        <el-input
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 4 }"
          v-model="formModel.description"
        ></el-input>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
import { mapState } from 'vuex'
export default {
  data: () => ({
    formModel: {
      name: null,
      description: null,
      price: null,
      room_type_id: null,
      city_id: null,
    },
    formRules: {
      name: [{ required: true, message: 'Please input name', trigger: 'blur' }],
      price: [
        { required: true, message: 'Please input price', trigger: 'blur' },
      ],
      room_type_id: [
        { required: true, message: 'Please input room type', trigger: 'blur' },
      ],
      city_id: [
        { required: true, message: 'Please input city', trigger: 'blur' },
      ],
      description: [
        {
          required: true,
          message: 'Please input description',
          trigger: 'blur',
        },
      ],
    },
  }),
  created() {
    let promises = [this.fetchCities(), this.fetchRoomTypes()]
    this.loading = true
    Promise.all(promises).then(() => {
      this.loading = false
    })
  },
  computed: {
    ...mapState({
      allCites: (state) => state.allCities,
      allRoomTypes: (state) => state.allRoomTypes,
    }),
  },
  methods: {
    async fetchCities() {
      try {
        await this.$store.dispatch('getCities')
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },

    async fetchRoomTypes() {
      try {
        await this.$store.dispatch('getRoomTypes')
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
    routeToPropertyList() {
      this.$router.push({ name: 'PropertyList', params: { type: 'myown' } })
    },
    async saveForm() {
      let propertyModel = this.$_.clone(this.formModel)
      let valid = await this.$refs['property-form'].validate()
      if (valid) {
        try {
          let response = await this.$axios.post('/addNewProperty', {
            properties: propertyModel,
          })
          if (response) {
            this.routeToPropertyList()
          }
        } catch (error) {
          this.$message.error('Server Error')
        }
      } else {
        this.$message.error('Error Occurred')
        return false
      }
    },
  },
}
</script>
