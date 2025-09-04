<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col overflow-auto relative">
    <div class="flex justify-between items-center mb-2">
      <h3 class="font-bold text-white text-lg md:text-2xl">Detected Objects</h3>

      <select
        v-model="selectedFilter"
        class="bg-gray-700 text-white text-sm md:text-base rounded px-2 py-1 focus:outline-none"
      >
        <option value="">All</option>
        <option v-for="item in filterOptions" :key="item" :value="item">
          {{ item }}
        </option>
      </select>
    </div>

    <ul class="grid grid-flow-col grid-rows-3 grid-cols-5 gap-2">
      <li
        v-for="(obj, index) in filteredObjects"
        :key="index"
        :class="getRelevanceColor(obj.relevance)"
        class="p-2 md:p-3 rounded bg-gray-700 text-sm md:text-base"
      >
        {{ obj.class }} - {{ (obj.confidence * 100).toFixed(2) }}%, 
        R:{{ obj.relevance }}, D:{{ obj.depth.toFixed(2) }}m
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps(["objectArray"]);

const objects = ref([]);
const selectedFilter = ref("");

// Dropdown options
const filterOptions = [
  "Bin",
  "Fallen bin",
  "Person",
  "Vehicle",
  "Animal",
  "Cyclist",
  "Fixed obstacle",
  "Ground hazards",
];

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

// Apply filtering
const filteredObjects = computed(() => {
  if (!selectedFilter.value) return sortedObjects.value;
  return sortedObjects.value.filter(
    (obj) => obj.class.toLowerCase() === selectedFilter.value.toLowerCase()
  );
});

watch(
  () => props.objectArray,
  (newArray) => {
    objects.value = newArray;
  }
);
</script>