<template>
  <div class="bg-gray-900 rounded-xl p-4 flex flex-col h-full">
    <span class="text-sm md:text-lg mb-2 text-gray-400 flex items-center gap-2">
      <template v-if="state.firstLocationReceived">
        {{ state.lastLocation.lat }}°, {{ state.lastLocation.lng }}°
      </template>
      <template v-else>
        <span class="flex items-center gap-2">
          Waiting for GPS
          <!-- Loading spinner -->
          <svg
            class="animate-spin h-4 w-4 text-green-400"
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
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            ></path>
          </svg>
        </span>
      </template>
    </span>

    <div
      class="bg-gray-700 flex-1 rounded-lg flex items-center justify-center min-h-[150px]"
    >
      <div id="mapContainer" class="w-full h-full"></div>
    </div>
  </div>
</template>

<script setup>
import { watch, onMounted, reactive } from "vue";
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

const state = reactive({
  firstLocationReceived: false,
  lastLocation: { lat: null, lng: null },
});

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

      state.firstLocationReceived = true;
      state.lastLocation = { lat, lng };

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
