<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import { url } from '../components/url'

const email = ref('')
const password = ref('')
const router = useRouter()
const toast = useToast()

const handleLogin = async () => {
  try {
    const response = await axios.post(`${url}/login`, {
      email: email.value,
      password: password.value,
    })
    if (email.value == 'girmadasingh@gmail.com' && password.value == 'Girmada@123') {
      toast.success('Welcome Girmada Shaw !!')
      setTimeout(() => {
        router.push('/admindashboard')
      }, 5500)
    }
    else if (response.data.token) {
      document.cookie = `token=${response.data.token}; path=/`
      toast.success('Login successful!')
      router.push('/userdashboard')
    } else {
      toast.error('Login failed.')
    }
  } catch (error) {
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.message || 'An error occurred'

      if (status === 401) {
        toast.error(message)
        setTimeout(() => {
          router.push('/signup')
        }, 5500)
      } else if (status === 402) {
        toast.error(message)
      } else if (status === 500) {
        toast.error('Something went wrong on the server.')
        console.error('Server Error:', error.response.data?.error)
      } else {
        toast.error('Unexpected error occurred.')
      }
    } else if (error.request) {
      // Request was made but no response received
      toast.error('No response from server.')
      console.error('Request error:', error.request)
    } else {
      // Something else went wrong setting up the request
      toast.error('Error while setting up login request.')
      console.error('Setup error:', error.message)
    }
  }
}
</script>


<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">Login</h1>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" v-model="email" id="email" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" v-model="password" id="password" required />
        </div>

        <button type="submit" class="login-btn">Login</button>
      </form>

      <p class="redirect">
        Don't have an account?
        <router-link to="/signup" class="signup-link">Sign Up</router-link>
      </p>
    </div>
  </div>
</template>


<style scoped>
.login-container {
  background-color: white;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  background-color: whitesmoke;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(107, 178, 161, 0.3);
  width: 100%;
  max-width: 400px;
}

.title {
  text-align: center;
  color: #6bb2a1;
  font-size: 2rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: #6bb2a1;
}

input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #7adec6;
  border-radius: 10px;
  background-color: #fff;
  outline: none;
  transition: border 0.2s ease;
}

input:focus {
  border-color: #6bb2a1;
}

.login-btn {
  background-color: #7adec6;
  color: #fff;
  font-weight: bold;
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.login-btn:hover {
  background-color: #6bb2a1;
}

.redirect {
  text-align: center;
  margin-top: 1rem;
  color: black;
}

.signup-link {
  margin-left: 4px;
  font-weight: 600;
  color: #7adec6;
  text-decoration: underline;
}
</style>
