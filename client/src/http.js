import axios from 'axios'
import Vue from 'vue'
import helper from 'mixins/helper'

const http = axios.create({
  baseURL: 'http://localhost:5000/api',
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
    return Promise.reject(error)
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
    }
  }
)

export default http
