<template>
  <div class="bg-gray-900 rounded-xl p-4 flex flex-col h-full relative">
    <div class="flex justify-between items-center mb-2">
      <h2 class="md:text-md lg:text-xl font-bold">Real-time Detection</h2>
    </div>
    <div class="flex-1 flex justify-center items-center overflow-hidden relative">
      <img 
        id="frame" 
        ref="videoFrame" 
        alt="Live Feed" 
        class="max-w-full max-h-full object-contain rounded-lg"
      />
      <div class="absolute bottom-2 right-2 p-2 rounded-lg text-xs text-white bg-gray-900/40 backdrop-blur-md shadow-lg">
        <p class="font-semibold mb-1">Color Represent</p>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded-full bg-red-600"></span>
          <span>Rating 5</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded-full bg-orange-400"></span>
          <span>Rating 4</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
          <span>Rating 3</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded-full bg-green-400"></span>
          <span>Rating 2</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded-full bg-cyan-400"></span>
          <span>Rating 1</span>
        </div>
      </div>
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
  const image = document.getElementById("frame");
  image.onload = function(){
    URL.revokeObjectURL(this.src)
  }
});
</script>