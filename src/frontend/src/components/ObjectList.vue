<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col h-full overflow-auto">
    <h3 class="font-bold text-white text-lg">Detected Objects</h3>
    <ul class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2 text-sm">
      <li
        v-for="(obj, index) in sortedObjects"
        :key="index"
        :class="getRelevanceColor(obj.relevance)"
        class="p-1 rounded"
      >
        {{ obj.class }} - {{ (obj.confidence * 100).toFixed(2) }}%, 
        R:{{ obj.relevance }}, D:{{ obj.depth.toFixed(2) }}m
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

const objects = ref([]);

let ws = null;

function getRelevanceColor(relevance) {
  switch (relevance) {
    case 5: return "text-red-600";
    case 4: return "text-orange-400";
    case 3: return "text-yellow-400";
    case 2: return "text-green-400";
    case 1: return "text-cyan-400";
    default: return "text-white";
  }
}

const sortedObjects = computed(() =>
  [...objects.value].sort((a, b) => b.relevance - a.relevance)
);

onMounted(() => {
  ws = new WebSocket("ws://127.0.0.1:8000/ws");

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (Array.isArray(data)) objects.value = data;
    } catch (err) {
      console.error("Error parsing WS data:", err);
    }
  };

  ws.onclose = () => console.log("WebSocket closed");
  ws.onerror = (err) => console.error("WebSocket error:", err);
});

onBeforeUnmount(() => {
  if (ws) ws.close();
});
</script>