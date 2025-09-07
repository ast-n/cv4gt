<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col h-full">
    <span class="text-sm md:text-lg mb-2 text-gray-400">
      {{ location && location.lat != null && location.lng != null
          ? `${location.lat}°, ${location.lng}°`
          : "Waiting for GPS..." }}
    </span>
    <div class="bg-gray-700 flex-1 rounded-lg flex items-center justify-center min-h-[150px]">
      <div id="mapContainer" class="w-full h-full"></div>
    </div>
  </div>
</template>

<script setup>
import { watch, onMounted } from "vue";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const props = defineProps({
  location: {
    type: Object,
    default: null,
  },
});

let map;
let marker = null; // marker only created when backend passes location
const baseLocation = [-37.82308, 145.03972]; // fallback center, no marker

onMounted(() => {
  // initialize map at base location
  map = L.map("mapContainer").setView(baseLocation, 17);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    minZoom: 2,
  }).addTo(map);
});

watch(
  () => props.location,
  (loc) => {
    // only update when backend passes valid location
    if (loc && loc.lat != null && loc.lng != null) {
      const lat = parseFloat(loc.lat);
      const lng = parseFloat(loc.lng);

      if (!marker) {
        marker = L.marker([lat, lng]).addTo(map);
      } else {
        marker.setLatLng([lat, lng]);
      }

      map.setView([lat, lng], 17);
    }
  },
  { deep: true }
);
</script>

<style>
#mapContainer {
  width: 100%;
  height: 100%;
}
</style>
