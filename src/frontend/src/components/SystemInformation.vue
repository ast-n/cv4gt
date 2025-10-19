<template>
  <div
    class="bg-gray-900 rounded-xl p-6 flex flex-col h-full w-full text-white"
  >
    <!-- Header -->
    <h2 class="md:text-lg lg:text-2xl font-bold self-start mb-6">
      System Information
    </h2>

    <!-- Metrics Row (centered) -->
    <div class="flex flex-row items-center justify-center space-x-8 w-full">
      <!-- Time -->
      <div class="flex flex-col items-center flex-1">
        <span class="text-gray-400 text-center">Current Time</span>
        <span class="text-sm font-mono text-green-400">{{ currentTime }}</span>
      </div>

      <!-- Video FPS (updated section) -->
      <div class="flex flex-col items-center flex-1">
        <span class="text-gray-400 text-center">Video FPS</span>
        <span
          class="text-sm font-mono"
          :class="videoFps < 20 ? 'text-red-400' : videoFps < 30 ? 'text-orange-400' : 'text-green-400'"
        >
          {{ videoFps.toFixed(0) }}
        </span>
      </div>

      <!-- CPU Usage -->
      <div class="flex flex-col items-center flex-1 w-full">
        <div class="flex items-center justify-center space-x-2 w-full">
          <img :src="cpuIcon" alt="CPU Icon" class="w-5 h-5 brightness-0 invert" />
          <span class="text-gray-400 text-sm">CPU Usage</span>
        </div>
        <span
          class="text-sm font-mono text-center"
          :class="cpuUsage >= 90 ? 'text-red-400' : cpuUsage >= 70 ? 'text-orange-400' : 'text-green-400'"
        >
          {{ cpuUsage }}%
        </span>
        <div class="w-full bg-gray-700 rounded-full h-2 mt-1">
          <div
            class="h-2 rounded-full transition-all duration-300"
            :class="cpuBarColor"
            :style="{ width: cpuUsage + '%' }"
          ></div>
        </div>
      </div>

      <!-- Memory Usage -->
      <div class="flex flex-col items-center flex-1 w-full">
        <div class="flex items-center justify-center space-x-2 w-full">
          <img :src="memoryIcon" alt="Memory Icon" class="w-5 h-5 brightness-0 invert" />
          <span class="text-gray-400 text-sm">Memory Usage</span>
        </div>
        <span
          class="text-sm font-mono text-center"
          :class="memoryPercent >= 90 ? 'text-red-400' : memoryPercent >= 70 ? 'text-orange-400' : 'text-green-400'"
        >
          {{ usedMB }}MB / {{ totalMB }}MB
        </span>
        <div class="w-full bg-gray-700 rounded-full h-2 mt-1">
          <div
            class="h-2 rounded-full transition-all duration-300"
            :class="memoryBarColor"
            :style="{ width: memoryPercent + '%' }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import cpuIcon from "../assets/cpu.png";
import memoryIcon from "../assets/memory.png";

/* Props passed from App.vue */
const props = defineProps({
  cpuUsage: { type: Number, default: 0 },
  usedMB: { type: Number, default: 0 },
  totalMB: { type: Number, default: 0 },
  videoFps: { type: Number, default: 0 }, // ✅ added
});

/* Local reactive state */
const currentTime = ref("");

let timeInterval = null;

/* TIME */
function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString([], { hour12: false });
}

/* Memory usage percentage */
const memoryPercent = computed(() => {
  if (!props.totalMB) return 0;
  return Math.min(100, ((props.usedMB / props.totalMB) * 100).toFixed(1));
});

/* Dynamic bar colors */
const cpuBarColor = computed(() => {
  if (props.cpuUsage >= 90) return "bg-red-500";
  if (props.cpuUsage >= 70) return "bg-orange-400";
  return "bg-green-500";
});

const memoryBarColor = computed(() => {
  if (memoryPercent.value >= 90) return "bg-red-500";
  if (memoryPercent.value >= 70) return "bg-orange-400";
  return "bg-green-500";
});

onMounted(() => {
  updateTime();
  timeInterval = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval);
});
</script>
