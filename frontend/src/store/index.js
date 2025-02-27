import { createStore } from 'vuex'

export default createStore({
  state: {
    // 定义应用的状态
    count: 0,
    user: null
  },
  getters: {
    // 获取状态的计算属性
    getCount: state => state.count,
    getUser: state => state.user
  },
  mutations: {
    // 更新状态的方法
    INCREMENT(state) {
      state.count++
    },
    SET_USER(state, user) {
      state.user = user
    }
  },
  actions: {
    // 异步操作
    async login({ commit }, credentials) {
      try {
        // 这里可以添加实际的登录API调用
        const response = await fetch('http://localhost:5000/api/test')
        const data = await response.json()
        commit('SET_USER', data)
        return data
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    }
  },
  modules: {
    // 模块化状态管理
  }
})