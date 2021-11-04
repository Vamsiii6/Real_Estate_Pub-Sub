<template>
  <div v-if="loading">
    <el-skeleton :rows="6" variant="rect" animated></el-skeleton>
  </div>
  <div v-else class="w-4/12">
    <div class="flex flex-row justify-between">
      <div class="h1-bold">Broker Topics Setup</div>
      <el-button type="primary" plain @click="updateBrokerTopics()"
        >Apply Changes</el-button
      >
    </div>
    <div class="mt-5">
      Broker 1
      <el-select
        v-model="broker1"
        multiple
        collapse-tags
        class="ml-5"
        placeholder="Choose Topics"
      >
        <el-option
          v-for="item in allCities"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        >
        </el-option>
      </el-select>
    </div>
    <div class="mt-5">
      Broker 2
      <el-select
        v-model="broker2"
        multiple
        collapse-tags
        placeholder="Choose Topics"
        class="ml-5"
      >
        <el-option
          v-for="item in allCities"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        >
        </el-option>
      </el-select>
    </div>
    <div class="mt-5">
      Broker 3
      <el-select
        v-model="broker3"
        multiple
        collapse-tags
        placeholder="Choose Topics"
        class="ml-5"
      >
        <el-option
          v-for="item in allCities"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        >
        </el-option>
      </el-select>
    </div>
    <div class="mt-5">
      Broker 4
      <el-select
        v-model="broker4"
        multiple
        collapse-tags
        placeholder="Choose Topics"
        class="ml-5"
      >
        <el-option
          v-for="item in allCities"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        >
        </el-option>
      </el-select>
    </div>
    <div class="mt-5"></div>
  </div>
</template>
<script>
export default {
  data: () => ({
    allCities: [],
    loading: true,
    broker1: [],
    broker2: [],
    broker3: [],
    broker4: [],
  }),
  mounted() {
    let promises = [this.fetchAllBrokerTopics(), this.fetchCities()]
    this.loading = true
    Promise.all(promises).then(() => {
      this.loading = false
      this.allCities = this.$_.clone(this.$store.state.allCities)
    })
  },
  methods: {
    async fetchCities() {
      try {
        await this.$store.dispatch('getCities')
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },

    async fetchAllBrokerTopics() {
      try {
        let response = await this.$axios.get(
          'http://localhost:5000/api/getAllBrokerTopics'
        )
        if (response?.data) {
          console.log(response?.data?.broker_topics)

          this.broker1 = (response?.data?.broker_topics || [])
            .filter((r) => r.broker_port == 5005)
            .map((r) => r.topic_id)
          this.broker2 = (response?.data?.broker_topics || [])
            .filter((r) => r.broker_port == 5006)
            .map((r) => r.topic_id)
          this.broker3 = (response?.data?.broker_topics || [])
            .filter((r) => r.broker_port == 5007)
            .map((r) => r.topic_id)
          this.broker4 = (response?.data?.broker_topics || [])
            .filter((r) => r.broker_port == 5008)
            .map((r) => r.topic_id)
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
    async updateBrokerTopics() {
      let uniqueList = new Set([
        ...this.broker1,
        ...this.broker2,
        ...this.broker3,
        ...this.broker4,
      ])
      for (let record of this.allCities) {
        if (!uniqueList.has(record.id)) {
          this.$message.error(`Kindly map ${record.name} to a broker`)
          return
        }
      }
      let payload = {
        brokerVsTopics: {
          5005: this.broker1,
          5006: this.broker2,
          5007: this.broker3,
          5008: this.broker4,
        },
      }
      try {
        let response = await this.$axios.post(
          'http://localhost:5000/api/manageBrokerTopics',
          payload
        )
        if (response) {
          this.$message.success('Broker Topics Updated Successfully')
        }
      } catch (error) {
        this.$message.error(error?.message || 'Server Error')
      }
    },
  },
}
</script>
