import axios from 'axios'
import Vue from 'vue'
import helper from 'mixins/helper'

const http = axios.create({
  baseURL: '',
  headers: {
    'Content-type': 'application/json',
  },
})

http.interceptors.request.use(
  (request) => {
    request.headers = request.headers || {}
    request.headers.common[
      'authorization'
    ] = `Bearer:${Vue.prototype.$cookie.get('authToken')}`
    return request
  },
  (error) => {
    throw error
  }
)

http.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Unauthorized
    if (error.response.status === 401) {
      helper.authLogout()
    } else {
      throw error
    }
  }
)

export default http
