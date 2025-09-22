<template>
  <div class="bg-gray-800 rounded-xl p-4 flex flex-col relative">
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

    <ul class="grid grid-rows-3 grid-flow-col grid-cols-5 gap-4.5 h-[350px]">
      <li
        v-for="(obj, index) in filteredObjects"
        :key="index"
        class="p-1.5 md:p-2 rounded bg-gray-700 text-xs md:text-sm flex flex-col gap-1 shadow-sm"
      >
        <!-- Top row: Icon + Badge -->
        <div class="flex items-center gap-1.5">
          <img
            v-if="iconMap[obj.class.toLowerCase()]"
            :src="iconMap[obj.class.toLowerCase()]"
            alt=""
            class="w-6 h-6 md:w-5 md:h-5 filter brightness-0 invert"
          />

          <!-- Category Badge -->
          <span
            class="px-3 py-1 rounded-full text-[30px] md:text-xs font-medium text-white"
            :style="{ backgroundColor: getRelevanceBgColor(obj.relevance) }"
          >
            {{ formatClassName(obj.class) }}
          </span>
        </div>

        <!-- Bottom row: Confidence Bar + Stats -->
        <div class="flex flex-col gap-0.5 w-full">
          <!-- Confidence Progress Bar -->
          <div class="w-full bg-gray-600 rounded-full h-1.5 overflow-hidden">
            <div
              class="h-1.5 rounded-full transition-all duration-300"
              :style="{
                width: (obj.confidence * 100).toFixed(0) + '%',
                backgroundColor: getRelevanceBgColor(obj.relevance),
              }"
            ></div>
          </div>

          <!-- Text row -->
          <div class="text-gray-300 text-[11px] md:text-xs">
            <span class="font-medium">{{ (obj.confidence * 100).toFixed(0) }}%</span> |
            <span :class="getRelevanceTextColor(obj.relevance)">R:{{ obj.relevance }}</span> |
            D:{{ obj.depth.toFixed(2) }}m
          </div>
        </div>
      </li>

      <!-- Placeholder if empty -->
      <li
        v-if="filteredObjects.length === 0"
        class="col-span-5 row-span-3 flex items-center justify-center text-white text-sm md:text-base"
      >
        No objects detected
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

// Import icons
import binIcon from "../assets/bin.png";
import carIcon from "../assets/car.png";
import cyclistIcon from "../assets/cyclist.png";
import pawIcon from "../assets/paw.png";
import userIcon from "../assets/user.png";

const props = defineProps(["objectArray"]);
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

// Icon mapping
const iconMap = {
  bin: binIcon,
  fallen_bin: binIcon,
  car: carIcon,
  vehicle: carIcon,
  cyclist: cyclistIcon,
  person: userIcon,
  animal: pawIcon,
  dog: pawIcon,
  cat: pawIcon,
};

// Format class names for display
function formatClassName(cls) {
  return cls.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// Relevance → badge background color
function getRelevanceBgColor(relevance) {
  switch (relevance) {
    case 5: return "#dc2626"; // red-600
    case 4: return "#f97316"; // orange-500
    case 3: return "#eab308"; // yellow-500
    case 2: return "#22c55e"; // green-500
    case 1: return "#06b6d4"; // cyan-500
    default: return "#6b7280"; // gray-500
  }
}

// Text color (for stats row)
function getRelevanceTextColor(relevance) {
  switch (relevance) {
    case 5: return "text-red-600";
    case 4: return "text-orange-400";
    case 3: return "text-yellow-400";
    case 2: return "text-green-400";
    case 1: return "text-cyan-400";
    default: return "text-white";
  }
}

// Sort objects by relevance descending
const sortedObjects = computed(() =>
  [...props.objectArray].sort((a, b) => b.relevance - a.relevance)
);

// Filter + limit to 15 items (3 rows x 5 columns)
const filteredObjects = computed(() => {
  let objs = selectedFilter.value
    ? sortedObjects.value.filter((obj) =>
        obj.class.toLowerCase().includes(selectedFilter.value.toLowerCase())
      )
    : sortedObjects.value;

  return objs.slice(0, 15); // max 15 items
});
</script>
