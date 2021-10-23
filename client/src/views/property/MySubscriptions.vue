<template>
  <div v-if="loading">
    <el-skeleton :rows="6" variant="rect" animated></el-skeleton>
  </div>
  <div v-else>
    <div class="h1-bold">My Subscriptions</div>
    <el-transfer
      class="mt-10 custom-transfer-panel"
      v-model="selectedCities"
      filterable
      :titles="['Available Cities', 'Subscribed Cities']"
      :props="{
        key: 'id',
        label: 'name',
      }"
      :data="allCities"
      :button-texts="['Unsubscribe', 'Subscribe']"
      @change="handleChange"
    >
    </el-transfer>
    <el-transfer
      class="mt-10 custom-transfer-panel"
      v-model="selectedRoomTypes"
      filterable
      :titles="['Available Room Types', 'Subscribed Room Types']"
      :props="{
        key: 'id',
        label: 'type',
      }"
      :data="allRoomTypes"
      :button-texts="['Unsubscribe', 'Subscribe']"
      @change="handleChange"
    >
    </el-transfer>
  </div>
</template>
<script>
import axios from 'axios'

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
      this.fetchAllSubscriptions(),
      this.fetchCities(),
      this.fetchRoomTypes(),
    ]
    this.loading = true
    Promise.all(promises).then(() => {
      this.allCities = this.$_.clone(this.$store.state.allCities)
      this.allRoomTypes = this.$_.clone(this.$store.state.allRoomTypes)
      this.loading = false
    })
    // this.apiData()
  },
  methods: {
    async fetchAllSubscriptions() {
      try {
        let response = await this.$axios.get(
          'http://localhost:5002/api/getAllSubscriptions'
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
    async manageSubscriptions(direction) {
      try {
        let response = await this.$axios.post(
          'http://localhost:5002/api/manageSubscriptions',
          {
            user_cities_rel: this.selectedCities,
            user_room_types_rel: this.selectedRoomTypes,
          }
        )
        if (response?.data) {
          this.$message.success(
            `${
              direction == 'right' ? 'Subscribed' : 'Unsubscribed'
            } successfully`
          )
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
    handleChange(value, direction, movedKeys) {
      console.log(value, direction, movedKeys)
      this.manageSubscriptions(direction)
    },
    async apiData() {
      const options = {
        method: 'GET',
        url: 'https://us-real-estate.p.rapidapi.com/v2/for-sale',
        params: {
          offset: '0',
          limit: '30',
          state_code: 'NY',
          city: 'Buffalo',
          sort: 'newest',
        },
        headers: {
          'x-rapidapi-host': 'us-real-estate.p.rapidapi.com',
          'x-rapidapi-key':
            '794a2152c5msh2b0ef914247c640p165355jsnd8fd78983d6f',
        },
      }
      axios
        .request(options)
        .then(function (response) {
          console.log(response)
        })
        .catch(function (error) {
          console.error(error)
        })
    },
  },
}
</script>
