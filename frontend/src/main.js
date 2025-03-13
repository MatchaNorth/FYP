import './assets/main.css'
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import SteamGameBlock from './components/SteamGameBlock.vue'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.component('steam-game-block', SteamGameBlock)
app.mount('#app')
