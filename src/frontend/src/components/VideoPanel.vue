<template>
  <div class="bg-gray-900 rounded-xl p-4 flex flex-col h-full relative">
    <div class="flex justify-between items-center mb-2">
      <h2 class="md:text-md lg:text-xl font-bold">Real-time Detection</h2>
    </div>
    <div class="flex-1 flex justify-center items-center overflow-hidden relative">
      <template v-if="state.firstConnection">
        <img 
          id="frame" 
          ref="videoFrame" 
          alt="Live Feed" 
          class="max-w-full max-h-full object-contain rounded-lg"
        />
      </template>
      <template v-else>
        <span class="flex flex-col items-center gap-2">
          <h2 class="md:text-md lg:text-xl">Waiting for connection...</h2>
          <!-- Loading spinner -->
          <svg
            class="animate-spin h-12 w-12 text-green-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="2"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M 4 12 a 8 8 0 0 1 8 -8 v 2 a 6 6 0 0 0 -6 6 H 4 z"
            ></path>
          </svg>
          <img id="frame"/>
        </span>
      </template>
      
      <div class="absolute bottom-2 right-2 p-2 rounded-lg text-xs text-white bg-gray-900/40 backdrop-blur-md shadow-lg">
        <p class="font-semibold mb-1">Color Represent</p>
        <div class="flex items-center space-x-2 mb-1">
          <span class="w-4 h-4 rounded-full bg-red-600"></span>
          <span class="text-sm">Rating 5</span>
        </div>
        <div class="flex items-center space-x-2 mb-1">
          <span class="w-4 h-4 rounded-full bg-orange-400"></span>
          <span class="text-sm">Rating 4</span>
        </div>
        <div class="flex items-center space-x-2 mb-1">
          <span class="w-4 h-4 rounded-full bg-yellow-400"></span>
          <span class="text-sm">Rating 3</span>
        </div>
        <div class="flex items-center space-x-2 mb-1">
          <span class="w-4 h-4 rounded-full bg-green-400"></span>
          <span class="text-sm">Rating 2</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-4 h-4 rounded-full bg-cyan-400"></span>
          <span class="text-sm">Rating 1</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, reactive } from "vue";

const props = defineProps(['currentFrameData'])

const currentTime = ref("");
const videoFrame = ref(null);

const state = reactive({
  firstConnection: false
});

watch(() => props.currentFrameData, async (newValue) => {
  state.firstConnection = true;
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