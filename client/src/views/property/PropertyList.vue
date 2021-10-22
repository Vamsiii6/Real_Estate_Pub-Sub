<template>
  <div class="h-full">
    <div class="flex flex-row justify-between">
      <div class="heading-1">Property List</div>
      <el-button
        v-if="!$_.isEmpty(allProperty)"
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
      <div class="mt-5">
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
        <div class="flex justify-center items-center">
          <InlineSvg
            src="real-estate-no-data"
            iconClass="icon size-100"
            class="h-3/6 w-3/6"
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
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data: () => ({
    allProperty: [],
    loading: true,
  }),
  mounted() {
    this.getAllPropertyRecord()
  },
  methods: {
    routeToForm() {
      this.$router.push({ name: 'PropertyForm' })
    },
    async getAllPropertyRecord() {
      try {
        this.loading = true
        let response = await this.$axios.get('/getAllProperty')
        this.allProperty = response?.data?.records
        this.loading = false
      } catch (error) {
        this.$message.error('Server Error')
      }
    },
  },
}
</script>
