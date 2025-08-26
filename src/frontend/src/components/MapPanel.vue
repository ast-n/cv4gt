<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col h-full">
    <span class="text-sm mb-2 text-gray-400">37.8124° S, 144.9623° E</span>
    <div class="bg-gray-700 flex-1 rounded-lg flex items-center justify-center min-h-[150px]">
      <div id="mapContainer" class="w-full h-full"></div>
    </div>
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";

export default {
  name: "MapPanel",
  data() {
    return {
      location: [-37.82308, 145.03972],
    };
  },
  mounted() {
    const map = L.map("mapContainer").setView(this.location, 17);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      minZoom: 15,
    }).addTo(map);
    L.marker(this.location).addTo(map);
  },
};
</script>