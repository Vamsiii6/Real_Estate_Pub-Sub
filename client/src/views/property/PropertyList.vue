<template>
  <div class="h-full" :key="type">
    <div class="flex flex-row justify-between">
      <div class="heading-1">Property List</div>
      <el-button
        v-if="!$_.isEmpty(allProperty) && type == 'myown'"
        type="primary"
        plain
        icon="el-icon-plus"
        @click="routeToForm()"
        >Add New Property</el-button
      >
    </div>
    <div
      v-if="loading"
      class="flex flex-row justify-center items-center h-full"
    >
      <div class="font-extrabold text-xl">Loading...</div>
    </div>
    <div
      v-else-if="$_.isEmpty(allProperty)"
      class="flex flex-col justify-center items-center h-full"
    >
      <div class="flex flex-col justify-center items-center">
        <InlineSvg
          src="real-estate-no-data"
          iconClass="icon size-100"
          class="h-40 w-40"
        />
        No Properties found
      </div>
      <div v-if="type == 'myown'" class="mt-5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          @click="routeToForm()"
          >Add New Property</el-button
        >
      </div>
    </div>
    <div v-else class="grid grid-cols-4 gap-6 mt-10">
      <div
        v-for="(property, index) in allProperty"
        :key="index"
        class="prop-container flex flex-col"
      >
        <div class="flex justify-center items-center image-container">
          <img
            v-if="!$_.isEmpty(property.image_url)"
            :src="property.image_url"
            class="h-full w-full rounded-md"
          />
          <InlineSvg
            v-else
            src="real-estate-no-data"
            iconClass="icon size-xl"
          />
        </div>
        <div class="p-5">
          <div class="prop-title flex flex-row justify-between">
            <div class="w-9/12 truncate">
              {{ property.name }}
            </div>
            <div class="price-tag">
              <div class="price-text truncate">{{ `$ ${property.price}` }}</div>
            </div>
          </div>
          <div class="mt-3 truncate">
            {{ property.description }}
          </div>
          <div class="mt-3 flex flex-row">
            <InlineSvg src="location" iconClass="icon size-m" class="mr-3" />
            {{ citiesMap[property.city_id] }}
          </div>
          <div class="mt-3 flex flex-row">
            <InlineSvg src="home" iconClass="icon size-m" class="mr-3" />
            {{ roomTypesMap[property.room_type_id] }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapState } from 'vuex'
export default {
  props: ['type'],
  data: () => ({
    allProperty: [],
    loading: true,
  }),
  created() {
    let promises = [
      this.fetchCities(),
      this.fetchRoomTypes(),
      this.getAllPropertyRecord(),
    ]
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
    citiesMap() {
      let citiesMap = {}
      this.allCites.forEach((record) => {
        citiesMap[record.id] = record.name
      })
      return citiesMap
    },
    roomTypesMap() {
      let roomTypesMap = {}
      this.allRoomTypes.forEach((record) => {
        roomTypesMap[record.id] = record.type
      })
      return roomTypesMap
    },
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
    routeToForm() {
      this.$router.push({ name: 'PropertyForm' })
    },
    async getAllPropertyRecord() {
      try {
        let response = await this.$axios.get(
          `/getAllProperty?mode=${this.type}`
        )
        this.allProperty = response?.data?.records
      } catch (error) {
        this.$message.error('Server Error')
      }
    },
  },
}
</script>
