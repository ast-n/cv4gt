<template>
  <div
    class="bg-gray-900 rounded-xl p-6 flex flex-col h-full w-full text-white"
  >
    <!-- Header -->
    <h2 class="md:text-lg lg:text-2xl font-bold self-start mb-15">
      System Information
    </h2>

    <!-- Metrics Row (centered) -->
    <div class="flex flex-row items-center justify-center space-x-16 w-full">
      <!-- Time -->
      <div class="flex flex-col items-center">
        <span class="text-gray-400 text-center">Current Time</span>
        <span class="text-xl font-mono text-green-400">{{ currentTime }}</span> 
      </div>

      <!-- FPS Counter -->
      <div class="flex flex-col items-center">
        <span class="text-gray-400 text-center">System FPS</span>
        <span
          class="text-xl font-mono"
          :class="fps < 30 ? 'text-red-400' : 'text-green-400'"
        >
          {{ fps }}
        </span>
      </div>

      <!-- CPU Usage -->
      <div class="flex flex-col items-center">
        <span class="text-gray-400 text-center">CPU Usage</span>
        <span class="text-xl font-mono text-green-400">{{ cpuUsage }}%</span>
      </div>

      <!-- Memory Usage -->
      <div class="flex flex-col items-center">
        <span class="text-gray-400">Memory Usage</span>
        <span class="text-xl font-mono text-green-400">
          {{ usedMB }}MB / {{ totalMB }}MB
        </span>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, onUnmounted } from "vue";

/* Props passed from App.vue */
const props = defineProps({
  cpuUsage: { type: Number, default: 0 },
  usedMB: { type: Number, default: 0 },
  totalMB: { type: Number, default: 0 },
});

/* Local reactive state */
const currentTime = ref("");
const fps = ref(0);

let frameCount = 0;
let lastTime = performance.now();
let rafId = null;
let timeInterval = null;

/* TIME */
function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString([], { hour12: false });
}

/* FPS calculation */
function measureFPS() {
  frameCount++;
  const now = performance.now();
  if (now - lastTime >= 1000) {
    fps.value = frameCount;
    frameCount = 0;
    lastTime = now;
  }
  rafId = requestAnimationFrame(measureFPS);
}

onMounted(() => {
  updateTime();
  timeInterval = setInterval(updateTime, 1000);
  rafId = requestAnimationFrame(measureFPS);
});

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval);
  if (rafId) cancelAnimationFrame(rafId);
});
</script>