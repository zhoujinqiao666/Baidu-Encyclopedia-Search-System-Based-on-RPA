import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'  // 1. 引入Element Plus
import 'element-plus/dist/index.css'    // 2. 引入样式文件

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)  // 3. 注册Element Plus

app.mount('#app')
