import Vue from 'vue'
import Vuex from 'vuex'
import _ from 'lodash'
import axios from '@/http'
Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    userDetails: {},
    allCities: [],
    allRoomTypes: [],
  },
  mutations: {
    setUser(state, userDetails) {
      state.userDetails = userDetails || {}
    },
    setCities(state, payload) {
      state.allCities = payload || []
    },
    setRoomTypes(state, payload) {
      state.allRoomTypes = payload || []
    },
  },
  actions: {
    async getCities({ commit, state }) {
      if (_.isEmpty(state.allCities)) {
        let response = await axios.get('/getAllCities')
        if (response?.data) {
          commit('setCities', response?.data?.cities || [])
        }
      } else {
        Promise.resolve('')
      }
    },
    async getRoomTypes({ commit, state }) {
      if (_.isEmpty(state.allRoomTypes)) {
        let response = await axios.get('/getAllRoomTypes')
        if (response?.data) {
          commit('setRoomTypes', response?.data?.roomTypes || [])
        }
      } else {
        Promise.resolve('')
      }
    },
  },
  modules: {},
  getters: {
    userDetails(state) {
      return state.userDetails
    },
    allCities(state) {
      return state.allCities
    },
    allRoomTypes(state) {
      return state.allRoomTypes
    },
  },
})
