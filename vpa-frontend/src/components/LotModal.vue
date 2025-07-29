<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { url } from './url'

const props = defineProps({
  mode: { type: String, required: true },
  lotData: { type: Object, default: null }
})

const emit = defineEmits(['saved', 'close'])

const form = ref({
  name: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: '',
  phone: '',
  total_slots: '',
  hourly_rate: '',
  is_active: true
})


watch(() => props.lotData, (newLot) => {
  if (props.mode === 'edit' && newLot) {
    form.value = { ...newLot, is_active: true }
  }
}, { immediate: true })

const saveLot = async () => {
  try {
    const endpoint = props.mode === 'create' ? '/createlot' : '/editlot'
    console.log("ENDPOINT: ", endpoint)
    const method = props.mode === 'create' ? 'post' : 'put'
    console.log("METHOD: ", method)
    await axios[method](`${url}${endpoint}`, form.value)
    emit('saved', form.value)
  } catch (err) {
    console.error('Error saving lot:', err)
  }
}



</script>

<template>
  <div class="modal-overlay">
    <div class="modal">
      <h3>{{ mode === 'create' ? 'Add New Lot' : 'Edit Lot' }}</h3>

      <div class="form-grid">
        <input v-model="form.name" placeholder="Lot Name" />
        <input v-model="form.address_line1" placeholder="Address Line 1" />
        <input v-model="form.address_line2" placeholder="Address Line 2" />
        <input v-model="form.city" placeholder="City" />
        <input v-model="form.state" placeholder="State" />
        <input v-model="form.postal_code" placeholder="Postal Code" />
        <input v-model="form.country" placeholder="Country" />
        <input v-model="form.phone" placeholder="Phone" />
        <input v-model="form.total_slots" placeholder="Total Slots" type="number" />
        <input v-model="form.hourly_rate" placeholder="Hourly Rate" type="number" step="0.01" />
        <label><input type="checkbox" v-model="form.is_active" /> Active Lot</label>
      </div>

      <div class="modal-actions">
        <button class="btn save" @click="saveLot">{{ mode === 'create' ? 'Create' : 'Save Changes' }}</button>
        <button class="btn cancel" @click="emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal {
  background: whitesmoke;
  padding: 2rem;
  border-radius: 12px;
  width: 500px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

h3 {
  color: #4B8C7A;
  margin-bottom: 1rem;
}

.form-grid {
  display: grid;
  gap: 0.6rem;
}

input {
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.9rem;
  margin-top: 1rem;
}

.btn.save {
  background: lightblue;
  color: solid black;
  font-weight: bolder;
  padding: 0.5em;
  cursor: pointer;
}
.btn.cancel {
  background: lightcoral;
  color: solid black;
  font-weight: bolder;
  padding: 0.5em;
  cursor: pointer;
}
</style>
