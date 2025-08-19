<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col gap-2 h-full">
    <div class="flex justify-between items-center mb-2">
      <h2 class="text-lg font-bold">Real-time Detection</h2>
      <span class="text-sm text-gray-400">{{ currentTime }}</span>
    </div>
    <div class="flex-1 flex justify-center items-center">
      <img ref="videoFrame" alt="Live Feed" class="max-w-full max-h-full rounded-lg"/>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const currentTime = ref("");
const videoFrame = ref(null);

function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString([], { hour12: false });
}

onMounted(() => {
  updateTime();
  const interval = setInterval(updateTime, 1000);

  const ws = new WebSocket("ws://localhost:8000/ws");
  ws.onmessage = (event) => {
    if (!(typeof event.data === "string")) {
      const blob = new Blob([event.data], { type: "image/jpeg" });
      videoFrame.value.src = URL.createObjectURL(blob);
    }
  };

  onUnmounted(() => {
    clearInterval(interval);
    ws.close();
  });
});
</script>