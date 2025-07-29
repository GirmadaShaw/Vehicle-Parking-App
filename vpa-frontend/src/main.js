import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import Toast, {POSITION } from "vue-toastification";
import 'vue-toastification/dist/index.css'

const options = {
    position: POSITION.TOP_CENTER,
    timeout: 5000,
    pauseonHover: true,
}

createApp(App).use(router).use(Toast, options).mount('#app')
