<template>
  <div class="counter">
    <h2>Vuex 计数器示例</h2>
    <p>当前计数：{{ count }}</p>
    <button @click="increment">增加</button>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { computed } from 'vue'

export default {
  name: 'Counter',
  setup() {
    const store = useStore()

    const count = computed(() => store.state.count)

    const increment = () => {
      store.commit('INCREMENT')
    }

    return {
      count,
      increment
    }
  }
}
</script>

<style scoped>
.counter {
  padding: 20px;
  text-align: center;
}

button {
  padding: 8px 16px;
  margin: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>