<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col gap-2 h-full">
    <div class="flex justify-between items-center mb-2">
      <h2 class="text-lg font-bold">Real-time Detection</h2>
      <span class="text-sm text-gray-400">{{ currentTime }}</span>
    </div>
    <div class="flex-1 flex justify-center items-center overflow-hidden">
      <img id="frame" ref="videoFrame" alt="Live Feed" class="max-w-full max-h-full object-contain rounded-lg"/>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";

const props = defineProps(['currentFrameData'])

const currentTime = ref("");
const videoFrame = ref(null);

watch(() => props.currentFrameData, async (newValue) => {
  const blob = new Blob([newValue], {type: "image/jpeg"});
  videoFrame.value.src = URL.createObjectURL(blob)
})

function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString([], { hour12: false });
}

onMounted(() => {
  updateTime();
  const interval = setInterval(updateTime, 1000);

  const image = document.getElementById("frame");
  image.onload = function(){
    URL.revokeObjectURL(this.src)
  }

  onUnmounted(() => {
    clearInterval(interval);
  });
});
</script>