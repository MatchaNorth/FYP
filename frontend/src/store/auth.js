import axios from 'axios'

const state = {
  user: null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: false
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
    state.isAuthenticated = !!user
  },
  SET_TOKEN(state, token) {
    state.token = token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },
  CLEAR_AUTH(state) {
    state.user = null
    state.token = null
    state.isAuthenticated = false
    localStorage.removeItem('token')
  }
}

const actions = {
  async login({ commit }, credentials) {
    try {
      const response = await axios.post('/api/auth/login', credentials)
      const { user, token } = response.data
      commit('SET_USER', user)
      commit('SET_TOKEN', token)
      return response
    } catch (error) {
      throw error
    }
  },

  async register({ commit }, userData) {
    try {
      const response = await axios.post('/api/auth/register', userData)
      return response
    } catch (error) {
      throw error
    }
  },

  async logout({ commit }) {
    try {
      await axios.post('/api/auth/logout')
      commit('CLEAR_AUTH')
    } catch (error) {
      console.error('Logout error:', error)
      // 即使请求失败，也清除本地认证状态
      commit('CLEAR_AUTH')
    }
  },

  async checkAuth({ commit }) {
    try {
      const response = await axios.get('/api/auth/user')
      const { user } = response.data
      commit('SET_USER', user)
      return user
    } catch (error) {
      commit('CLEAR_AUTH')
      throw error
    }
  }
}

const getters = {
  isAuthenticated: state => state.isAuthenticated,
  currentUser: state => state.user,
  token: state => state.token
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}