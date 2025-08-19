<template>
  <div class="flex flex-col h-screen bg-gray-900 text-white p-4 gap-4">

    <!-- Top Section: Video + Map -->
    <div class="flex flex-1 gap-4 flex-col md:flex-row">
      <VideoPanel class="flex-[4] min-h-[200px]" />
      <MapPanel class="flex-[2] min-h-[200px]" />
    </div>

    <!-- Bottom Section: Object List -->
    <div class="flex-shrink-0">
      <ObjectList class="w-full" />
    </div>

  </div>
</template>

<script setup>
import VideoPanel from './components/VideoPanel.vue'
import ObjectList from './components/ObjectList.vue'
import MapPanel from './components/MapPanel.vue'
</script>