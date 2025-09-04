<template>
  <div class="flex flex-col h-screen bg-gray-900 text-white p-2 md:p-4 gap-3 text-base md:text-lg">

    <!-- Top Section: Video + Map -->
    <div class="flex flex-1 gap-4 flex-col md:flex-row">
      <VideoPanel class="flex-[4] min-h-[180px] md:min-h-[400px]" :current-frame-data="frameData" />
      <MapPanel class="flex-[2] min-h-[180px] md:min-h-[400px]" />
    </div>

    <!-- Bottom Section: Object List -->
    <div class="flex-[0.5] min-h-[180px] md:min-h-[200px] overflow-auto">
      <ObjectList class="w-full" :object-array="objects" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, onBeforeUnmount, ref } from "vue";

import VideoPanel from './components/VideoPanel.vue'
import ObjectList from './components/ObjectList.vue'
import MapPanel from './components/MapPanel.vue'

const frameData  = ref(null)
const objects = ref([])

onMounted(() => {
  const ws = new WebSocket("ws://localhost:8000/ws");
  ws.onmessage = (event) => {
    if (!(typeof event.data === "string")) {
      frameData.value = event.data
    } else {
      try {
        const data = JSON.parse(event.data);
        if (Array.isArray(data)) objects.value = data;
      } catch (err) {
        console.error("Error parsing WS data:", err);
      }
    }
  };

  ws.onclose = () => console.log("WebSocket closed");
  ws.onerror = (err) => console.error("WebSocket error:", err);

  onUnmounted(() => {
    ws.close();
  })
})

onBeforeUnmount(() => {
  if (ws) ws.close();
});
</script>