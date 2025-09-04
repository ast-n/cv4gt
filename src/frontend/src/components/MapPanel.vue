<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col h-full">
    <span class="text-sm md:text-lg mb-2 text-gray-400">37.8124° S, 144.9623° E</span>
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
      map: null,
      ws: null,
      location: [-37.82308, 145.03972], // base location
    };
  },
  mounted() {
    this.map = L.map("mapContainer").setView(this.location, 17);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      minZoom: 15,
    }).addTo(this.map);

    const baseMarker = L.marker(this.location).bindPopup("Base Location");
    baseMarker.addTo(this.map);

    this.connectWebSocket();
  },
  methods: {
    connectWebSocket() {
      this.ws = new WebSocket("ws://127.0.0.1:8000/ws");

      this.ws.onmessage = (event) => {
        if (typeof event.data === "string") {
          try {
            const msg = JSON.parse(event.data);
            console.log("Received data from backend:", msg);
          } catch (e) {
            console.error("JSON parse error:", e);
          }
        }
      };

      this.ws.onclose = () => {
        console.warn("WebSocket closed, retrying in 2s...");
        setTimeout(this.connectWebSocket, 2000);
      };
    },
  },
};
</script>

<style>
#mapContainer {
  width: 100%;
  height: 100%;
}
</style>