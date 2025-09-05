<template>
  <div class="flex flex-col h-screen bg-gray-900 text-white p-4 gap-4">

    <!-- Top Section: Video + Map -->
    <div class="flex flex-1 gap-4 flex-col md:flex-row">
      <VideoPanel class="flex-[4] min-h-[200px]" :current-frame-data="frameData" />
      <MapPanel class="flex-[2] min-h-[200px]"/>
    </div>

    <!-- Bottom Section: Object List -->
    <div class="flex-[0.4] min-h-[150px] overflow-auto">
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
const jsondata = ref("")

onMounted(() => {
  const ws = new WebSocket("ws://localhost:8000/ws");
  ws.onmessage = (event) => {
    if (!(typeof event.data === "string")) {
      frameData.value = event.data
    } else {
      try {
        jsondata.value = JSON.parse(event.data);
        if (jsondata.value.event === 'objects') {
          if (Array.isArray(jsondata.value.content)) objects.value = jsondata.value.content;
        } else if (jsondata.value.event === 'location') {
          //Whatever code needed to pass to map
        }
        
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