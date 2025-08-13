<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col gap-2 flex-[2]">
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-bold">Real-time Detection</h2>
      <span class="text-sm text-gray-400">{{ currentTime }}</span>
    </div>

    <div class="bg-black rounded-xl flex-1 flex items-center justify-center min-h-[24rem]">
      <span class="text-gray-500">[ Live Video Placeholder ]</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const currentTime = ref('')

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => {
  updateTime()
  const interval = setInterval(updateTime, 1000)
  onUnmounted(() => clearInterval(interval))
})
</script>