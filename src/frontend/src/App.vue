<template>
  <div
    class="flex flex-col w-screen bg-gray-600 text-white p-2 md:p-4 gap-3 text-base md:text-lg h-auto sm:h-screen overflow-y-auto sm:overflow-hidden overflow-x-hidden">
    <!-- Main Section -->
    <div class="flex flex-1 flex-col sm:flex-row gap-4 sm:overflow-hidden">
      
      <!-- Left column: Video + New Component (wider) -->
      <div class="flex flex-col flex-[3] gap-3 sm:overflow-hidden">
        <VideoPanel class="min-h-[200px] sm:min-h-0 flex-[7]" :current-frame-data="frameData" />
        <NewComponent class="min-h-[150px] sm:min-h-0 flex-[3]"/>
      </div>

      <!-- Right column: Map + Object List -->
      <div class="flex flex-col flex-[2] gap-3 h-[400px] sm:h-full">
        <MapPanel class="flex-1 min-h-[200px]" :location="location"/>
        <ObjectList class="flex-[2] w-full sm:w-full overflow-auto" :object-array="objects"/>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, onBeforeUnmount, ref } from "vue";

import VideoPanel from './components/VideoPanel.vue'
import ObjectList from './components/ObjectList.vue'
import MapPanel from './components/MapPanel.vue'
import NewComponent from './components/New.vue'

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