// router.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from './components/Home.vue'
import Lot from "./components/BookLot.vue"
import Login from './components/Login.vue'
import Signup from './components/Signup.vue'
import UserDashboard from './components/UserDashboard.vue'
import AdminDashboard from './components/AdminDashboard.vue'

const routes = [
  { path: '/', component: Home, name: 'Home' },
  { path: '/booklot', component: Lot, name: 'Lot'},
  {path: '/login', component: Login, name: 'Login'},
  {path: '/signup', component: Signup, name: 'Signup'},
  {path: '/userdashboard', component: UserDashboard, name: 'UserDashboard'},
  {path: '/admindashboard', component: AdminDashboard, name: 'AdminDashboard'},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
