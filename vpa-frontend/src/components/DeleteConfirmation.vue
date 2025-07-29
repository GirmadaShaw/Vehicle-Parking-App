<script setup>
import axios from 'axios'
import { url } from './url'

const props = defineProps({
  lotName: { type: String, required: true }
})

const emit = defineEmits(['deleted', 'close'])

const confirmDelete = async () => {
  try {
    await axios.post(`${url}/deletelot`, { name: props.lotName })
    emit('deleted', props.lotName)
  } catch (err) {
    console.error('Error deleting lot:', err)
  }
}
</script>

<template>
  <div class="modal-overlay">
    <div class="modal delete-modal">
      <h3>⚠️ Confirm Delete</h3>
      <p>Are you sure you want to delete <strong>{{ lotName }}</strong>?</p>
      <div class="modal-actions">
        <button class="btn delete" @click="confirmDelete">Yes, Delete</button>
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

.delete-modal {
  background: #e7e5e5;
  padding: 2rem;
  border-radius: 12px;
  width: 400px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

h3 {
  color: #4B8C7A;
  margin-bottom: 0.5rem;
  font-weight: bolder ;
}

p {
  color: #6BB2A1;
  font-weight: light;
  margin-bottom: 1rem;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 0.9rem;
}

.btn.delete {
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
