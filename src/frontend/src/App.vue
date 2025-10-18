<template>
  <div
    class="flex flex-col w-screen bg-gray-600 text-white p-2 md:p-4 gap-3 text-base md:text-lg h-auto sm:h-screen overflow-y-auto sm:overflow-hidden overflow-x-hidden"
  >
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
        <NewComponent
          class="flex-1 w-full sm:w-full overflow-auto"
          :cpu-usage="cpuUsage"
          :used-m-b="usedMB"
          :total-m-b="totalMB"
          :video-fps="videoFPS"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

import VideoPanel from './components/VideoPanel.vue'
import ObjectList from './components/ObjectList.vue'
import MapPanel from './components/MapPanel.vue'
import NewComponent from './components/SystemInformation.vue'

/* Reactive state */
const frameData = ref(null);
const objects = ref([]);
const location = ref(null);
const jsondata = ref("");

// System metrics
const cpuUsage = ref(0);
const usedMB = ref(0);
const totalMB = ref(0);
const videoFPS = ref(0);

let lastFrameTime = performance.now();
let frameCount = 0;

let ws;
let reconnectDelay = 1000;
let reconnectInterval;

function connectWebSocket() {
  ws = new WebSocket("ws://localhost:8000/ws");
  console.log("Opening WebSocket...");

  ws.onopen = () => {
    console.log("Connected to WebSocket.");
    clearInterval(reconnectInterval);
    reconnectInterval = null;
    reconnectDelay = 1000;
  };

  ws.onmessage = (event) => {
    if (typeof event.data !== "string") {
      // Handle binary frame data
      frameData.value = event.data;
      calculateVideoFPS();
    } else {
      handleJSON(event.data);
    }
  };

  ws.onclose = () => {
    console.log("Not connected to WebSocket. Attempting reconnection...");
    startReconnection();
  };

  ws.onerror = (err) => {
    console.error("WebSocket error:", err);
    ws.close();
  };
}

function calculateVideoFPS() {
  const now = performance.now();
  frameCount++;
  if (now - lastFrameTime >= 1000) {
    videoFPS.value = frameCount;
    frameCount = 0;
    lastFrameTime = now;
  }
}

function handleJSON(data) {
  try {
    jsondata.value = JSON.parse(data);
    const event = jsondata.value.event;

    switch (event) {
      case "objects":
        if (Array.isArray(jsondata.value.content))
          objects.value = jsondata.value.content;
        break;
      case "location":
        location.value = jsondata.value.content;
        break;
      case "system":
        const sys = jsondata.value.content;
        cpuUsage.value = sys.cpu || 0;
        usedMB.value = sys.usedMB || 0;
        totalMB.value = sys.totalMB || 0;
        break;
    }
  } catch (err) {
    console.error("Error parsing WS data:", err);
  }
}

function startReconnection() {
  if (reconnectInterval) return;
  reconnectInterval = setInterval(() => {
    if (ws.readyState === WebSocket.CLOSED) {
      console.log("Reconnecting WebSocket...");
      connectWebSocket();
      reconnectDelay = Math.min(reconnectDelay * 2, 30000); // exponential backoff
    }
  }, reconnectDelay);
}

function closeWebSocket() {
  if (ws) {
    ws.close();
    clearInterval(reconnectInterval);
  }
}

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  closeWebSocket();
});
</script>
