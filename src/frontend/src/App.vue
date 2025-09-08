<template>
  <div class="flex flex-col h-screen bg-gray-600 text-white p-2 md:p-4 gap-3 text-base md:text-lg">

    <!-- Top Section: Video + Map -->
    <div class="flex flex-1 gap-4 flex-col md:flex-row">
      <VideoPanel class="flex-[3] min-h-[80px] md:min-h-[300px]" :current-frame-data="frameData" />
      <MapPanel class="flex-[2] min-h-[80px] md:min-h-[250px]" :location="location" />
    </div>

    <!-- Bottom Section: Object List -->
    <div>
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
const location = ref(null)

let ws

onMounted(() => {
  ws = new WebSocket("ws://localhost:8000/ws");
  ws.onmessage = (event) => {
    if (!(typeof event.data === "string")) {
      frameData.value = event.data
    } else {
      try {
        jsondata.value = JSON.parse(event.data);
        if (jsondata.value.event === 'objects') {
          if (Array.isArray(jsondata.value.content)) objects.value = jsondata.value.content;
        } else if (jsondata.value.event === 'location') {
          location.value = jsondata.value.content
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