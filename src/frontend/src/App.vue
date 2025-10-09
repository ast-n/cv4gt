<template>
  <div
    class="flex flex-col w-screen bg-gray-600 text-white p-2 md:p-4 gap-3 text-base md:text-lg h-auto sm:h-screen overflow-y-auto sm:overflow-hidden overflow-x-hidden">
    <!-- Main Section -->
    <div class="flex flex-1 flex-col sm:flex-row gap-4 sm:overflow-hidden">
      
      <!-- Left column: Video + Detected objects -->
      <div class="flex flex-col flex-[3] gap-3 sm:overflow-hidden">
        <VideoPanel class="min-h-[200px] sm:min-h-0 flex-[8]" :current-frame-data="frameData" />
        <ObjectList class="min-h-[150px] sm:min-h-0 flex-[4]" :object-array="objects"/>
      </div>

      <!-- Right column: Map + system information -->
      <div class="flex flex-col flex-[2] gap-3 h-[400px] sm:h-full">
        <MapPanel class="flex-3 min-h-[200px]" :location="location"/>
        <NewComponent class="flex-1 w-full sm:w-full overflow-auto" :cpu-usage="cpuUsage" :used-m-b="usedMB" :total-m-b="totalMB"/>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";

import VideoPanel from './components/VideoPanel.vue'
import ObjectList from './components/ObjectList.vue'
import MapPanel from './components/MapPanel.vue'
import NewComponent from './components/SystemInformation.vue'

/* Reactive state */
const frameData  = ref(null);
const objects = ref([]);
const location = ref(null);
const jsondata = ref("");

// System metrics
const cpuUsage = ref(0);
const usedMB = ref(0);
const totalMB = ref(0);

let ws;

onMounted(() => {
  ws = new WebSocket("ws://localhost:8000/ws");

  ws.onmessage = (event) => {
    if (!(typeof event.data === "string")) {
      frameData.value = event.data;
    } else {
      try {
        jsondata.value = JSON.parse(event.data);

        // Objects
        if (jsondata.value.event === 'objects') {
          if (Array.isArray(jsondata.value.content)) objects.value = jsondata.value.content;

        // Location
        } else if (jsondata.value.event === 'location') {
          location.value = jsondata.value.content;

        // System info: CPU + Memory
        } else if (jsondata.value.event === 'system') {
          cpuUsage.value = jsondata.value.content.cpu || 0;
          usedMB.value = jsondata.value.content.usedMB || 0;
          totalMB.value = jsondata.value.content.totalMB || 0;
        }

      } catch (err) {
        console.error("Error parsing WS data:", err);
      }
    }
  };

  ws.onclose = () => console.log("WebSocket closed");
  ws.onerror = (err) => console.error("WebSocket error:", err);
});

onUnmounted(() => {
  if (ws) ws.close();
});
</script>