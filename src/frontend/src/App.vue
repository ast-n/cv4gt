<template>
  <div class="flex h-screen bg-gray-900 text-white p-4 gap-4">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col gap-4">
      <!-- Video Panel -->
      <VideoPanel class="flex-[2]" />

      <!-- Bottom Section -->
      <div class="flex gap-4 flex-1">
        <ObjectList class="flex-1" />
        <MapPanel class="flex-[2]" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import VideoPanel from './components/VideoPanel.vue'
import ObjectList from './components/ObjectList.vue'
import MapPanel from './components/MapPanel.vue'
</script>

<style>
body {
  margin: 0;
}
</style>