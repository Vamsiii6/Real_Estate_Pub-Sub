<template>
  <div v-if="loading">
    <el-skeleton :rows="6" variant="rect" animated></el-skeleton>
  </div>
  <div v-else>
    <div class="h1-bold">Manage Advertisements</div>
    <el-transfer
      class="mt-10 custom-transfer-panel"
      v-model="selectedCities"
      filterable
      :titles="['Available Cities', 'My Cities']"
      :props="{
        key: 'id',
        label: 'name',
      }"
      :data="allCities"
      :button-texts="['Deadvertise', 'Advertise']"
      @change="handleChange"
    >
    </el-transfer>
    <el-transfer
      class="mt-10 custom-transfer-panel"
      v-model="selectedRoomTypes"
      filterable
      :titles="['Available Room Types', 'My Room Types']"
      :props="{
        key: 'id',
        label: 'type',
      }"
      :data="allRoomTypes"
      :button-texts="['Deadvertise', 'Advertise']"
      @change="handleChange"
    >
    </el-transfer>
  </div>
</template>
<script>
export default {
  data: () => ({
    selectedCities: [],
    allCities: [],
    selectedRoomTypes: [],
    allRoomTypes: [],
    loading: true,
  }),
  mounted() {
    let promises = [
      this.fetchAllAds(),
      this.fetchCities(),
      this.fetchRoomTypes(),
    ]
    this.loading = true
    Promise.all(promises).then(() => {
      this.allCities = this.$_.clone(this.$store.state.allCities)
      this.allRoomTypes = this.$_.clone(this.$store.state.allRoomTypes)
      this.loading = false
    })
  },
  methods: {
    async fetchAllAds() {
      try {
        let response = await this.$axios.get(
          'http://localhost:5000/api/getAllAvertisements'
        )
        if (response?.data) {
          this.selectedCities = (response?.data?.cities || []).map(
            (r) => r.city_id
          )
          this.selectedRoomTypes = (response?.data?.room_types || []).map(
            (r) => r.room_type_id
          )
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
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
    async manageAdvertisements(direction) {
      try {
        let response = await this.$axios.post(
          'http://localhost:5000/api/manageAdvertisements',
          {
            adv_cities_rel: this.selectedCities,
            adv_room_types_rel: this.selectedRoomTypes,
          }
        )
        if (response?.data) {
          this.$message.success(
            `${
              direction == 'right'
                ? 'Advertisement data added'
                : 'Deadvertisement data removed'
            } successfully`
          )
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
    handleChange(value, direction, movedKeys) {
      console.log(value, direction, movedKeys)
      this.manageAdvertisements(direction)
    },
  },
}
</script>
