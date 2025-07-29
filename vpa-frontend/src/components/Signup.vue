<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { url } from '../components/url'

const router = useRouter()
const toast = useToast()

const form = ref({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  phone: ''
})

const otp = ref(['', '', '', ''])
const showOtpInput = ref(false)

async function handleSignup() {
  try {
    const response = await axios.post(`${url}/signup`, {
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      phone: form.value.phone
    });

    if (response.status === 200 && response.data.success) {
      toast.success(response.data.message);
      showOtpInput.value = true;
    } else {
      toast.error(response.data.message || 'Signup failed');
    }

  } catch (error) {
    if (error.response) {
      const status = error.response.status;
      const message = error.response.data?.message || 'Something went wrong';

      if (status === 401) {
        toast.error(message);
      } else if (status === 500) {
        toast.error("Server error. Please try again later."); // internal backend error
      } else {
        toast.error("Unexpected error occurred.");
      }
    } else {
      toast.error("Network error. Please check your internet connection.");
    }

    console.error("Signup Error:", error);
  }
}


function focusNext(index, event) {
  if (event.target.value && index < otp.value.length - 1) {
    event.target.nextElementSibling?.focus()
  }
}

async function verifyOtp() {
  const code = otp.value.join('');
  console.log("In signup.vue , verifyOtp method, code is:", code);
  
  if (code.length !== 4) {
    toast.error("Enter complete 4-digit OTP");
    return;
  }

  try {
    const response = await axios.post(`${url}/verify-otp`, {
        email: form.value.email,
        otp: code
    });

    // Success
    if (response.status === 200 && response.data.success) {
      toast.success("OTP Verified. Redirecting to Dashboard...");
      router.push('/userdashboard');
    } else {
      toast.error(response.data.message || "OTP verification failed.");
    }

  } catch (error) {
    if (error.response) {
      const status = error.response.status;
      const message = error.response.data?.message || "Something went wrong";

      if (status === 401) {
        toast.error(message); // Known issues like invalid OTP, session expired, etc.
      } else if (status === 500) {
        toast.error("Server error. Please try again later."); // Internal error
      } else {
        toast.error("An unexpected error occurred.");
      }
    } else {
      toast.error("Network error. Please check your connection.");
    }
  }
}
</script>


<template>
  <div class="signup-container">
    <!-- Signup Form -->
    <form v-if="!showOtpInput" @submit.prevent="handleSignup" class="signup-form">
      <h2 class="title">Sign Up</h2>

      <input v-model="form.username" type="text" placeholder="Username" required />
      <input v-model="form.email" type="email" placeholder="Email" required />
      <input v-model="form.password" type="password" placeholder="Password" required />
      <input v-model="form.first_name" type="text" placeholder="First Name" required />
      <input v-model="form.last_name" type="text" placeholder="Last Name" required />
      <input v-model="form.phone" type="text" placeholder="Phone" required />

      <button type="submit" class="submit-btn">Sign Up</button>

      <p class="redirect">
        Already have an account?
        <router-link to="/login" class="link">Login here</router-link>
      </p>
    </form>

    <!-- OTP Verification -->
    <div v-else class="otp-section">
      <h3>Enter OTP sent to your email</h3>
      <div class="otp-inputs">
        <input
          v-for="(digit, index) in otp"
          :key="index"
          maxlength="1"
          type="text"
          v-model="otp[index]"
          @input="focusNext(index, $event)"
        />
      </div>
      <button class="submit-btn" @click="verifyOtp">Verify</button>
    </div>
  </div>
</template>


<style scoped>
.signup-container {
  min-height: 100vh;
  background: white;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 1.5rem;
}

.signup-form {
  background: whitesmoke;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 0 10px rgba(122, 222, 198, 0.3);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 400px;
}

.title {
  color: #6BB2A1;
  text-align: center;
  margin-bottom: 1rem;
}

input {
  padding: 0.75rem;
  border: 1px solid #7ADEC6;
  border-radius: 8px;
  background: #fff;
}

.submit-btn {
  background: #7ADEC6;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: bold;
}

.submit-btn:hover {
  background: #6BB2A1;
}

.redirect {
  text-align: center;
  font-size: 0.9rem;
}

.link {
  color: #6BB2A1;
  text-decoration: underline;
}

.otp-section {
  margin-top: 2rem;
  background: whitesmoke;
  padding: 1rem;
  border-radius: 10px;
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.otp-inputs {
  display: flex;
  justify-content: space-between;
  margin: 1rem 0;
}

.otp-inputs input {
  width: 50px;
  height: 50px;
  font-size: 1.5rem;
  text-align: center;
  border: 2px solid #7ADEC6;
  border-radius: 8px;
}
</style>
