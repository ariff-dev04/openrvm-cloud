<script setup lang="ts">
import { computed } from 'vue'
import type { StationGroup } from '../../core/types'

const props = defineProps<{
  station: StationGroup
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'back'): void
  (e: 'drop', payload: { deviceNo: string; positionNo: number; weight: number; label: string }): void
}>()

const googleMapsUrl = computed(() => {
  return `https://www.google.com/maps/dir/?api=1&destination=${props.station.latitude},${props.station.longitude}`
})

const wazeUrl = computed(() => {
  return `https://waze.com/ul?ll=${props.station.latitude},${props.station.longitude}&navigate=yes`
})

const osmEmbedUrl = computed(() => {
  const lat = props.station.latitude
  const lon = props.station.longitude
  return `https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.005}%2C${lat - 0.005}%2C${lon + 0.005}%2C${lat + 0.005}&layer=mapnik&marker=${lat}%2C${lon}`
})
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Top Header -->
    <div class="flex items-center justify-between">
      <button @click="emit('back')" class="px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-bold shadow-sm hover:bg-slate-50">
        ← Back to Stations
      </button>
      <span :class="station.isOnline ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'" class="px-2.5 py-1 rounded-full text-xs font-bold">
        ● {{ station.isOnline ? 'Station Online' : 'Under Maintenance' }}
      </span>
    </div>

    <!-- Station Overview & Interactive Map Card -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="h-44 w-full bg-slate-200 relative">
        <iframe :src="osmEmbedUrl" class="w-full h-full border-0" loading="lazy"></iframe>
        <div class="absolute bottom-2 right-2 bg-slate-900/80 text-white px-2.5 py-1 rounded-lg text-[10px] font-mono">
          GPS: {{ station.latitude.toFixed(4) }}, {{ station.longitude.toFixed(4) }}
        </div>
      </div>

      <div class="p-4 space-y-3">
        <div class="flex justify-between items-start">
          <div>
            <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-600">{{ station.zone }}</span>
            <h2 class="text-lg font-extrabold text-slate-900">{{ station.stationName }}</h2>
            <p class="text-xs text-slate-500 mt-0.5">📍 {{ station.address }}</p>
          </div>
          <span class="px-2.5 py-1 bg-slate-100 rounded-lg text-xs font-bold text-slate-700 shrink-0">
            {{ station.distanceKm }} km away
          </span>
        </div>

        <!-- Direct Native Maps Navigation Buttons -->
        <div class="grid grid-cols-2 gap-2 pt-2">
          <a :href="googleMapsUrl" target="_blank" rel="noopener"
            class="py-2.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-1.5 shadow transition">
            <span>🗺️</span><span>Google Maps</span>
          </a>
          <a :href="wazeUrl" target="_blank" rel="noopener"
            class="py-2.5 px-3 bg-sky-500 hover:bg-sky-400 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-1.5 shadow transition">
            <span>🚗</span><span>Open in Waze</span>
          </a>
        </div>
      </div>
    </div>

    <!-- Detailed Hardware Compartments Breakdown -->
    <div class="space-y-3">
      <h3 class="font-bold text-sm text-slate-800">♻️ Available Machine Compartments ({{ station.bins.length }})</h3>

      <div v-for="bin in station.bins" :key="bin.deviceNo + '-' + bin.positionNo"
        class="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-3">
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-base">{{ bin.deviceType === 'UCO_OIL' ? '🛢️' : '♻️' }}</span>
              <h4 class="font-bold text-sm text-slate-900">Bin #{{ bin.positionNo }}: {{ bin.rubbishTypeName }}</h4>
            </div>
            <p class="text-[11px] font-mono text-slate-400 mt-0.5">
              Hardware ID: {{ bin.deviceNo }} ({{ bin.deviceType === 'UCO_OIL' ? 'Fluid Sensor Unit' : '2-Door Camera RVM' }})
            </p>
          </div>
          <span class="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg text-xs font-extrabold">
            +{{ bin.ratePerKg }} pts/kg
          </span>
        </div>

        <div class="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1.5 text-xs">
          <div class="flex justify-between">
            <span class="text-slate-500 font-medium">Current Compartment Load:</span>
            <span class="font-bold text-slate-800">{{ bin.currentWeight }} kg / {{ bin.maxWeight }} kg ({{ bin.fillPercent }}%)</span>
          </div>
          <div class="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
            <div :class="bin.fillPercent >= 95 ? 'bg-rose-500' : (bin.fillPercent >= 80 ? 'bg-amber-500' : 'bg-emerald-500')"
              class="h-full transition-all" :style="{ width: bin.fillPercent + '%' }"></div>
          </div>
          <div class="flex justify-between text-[11px] pt-1">
            <span class="text-slate-400">Remaining Capacity: {{ (bin.maxWeight - bin.currentWeight).toFixed(1) }} kg</span>
            <span :class="bin.fillPercent >= 80 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold'">{{ bin.statusLabel }}</span>
          </div>
        </div>

        <button
          v-if="station.isOnline && bin.fillPercent < 100"
          :disabled="loading"
          @click="emit('drop', { deviceNo: bin.deviceNo, positionNo: bin.positionNo, weight: 1.25, label: bin.rubbishTypeName })"
          class="w-full py-2.5 bg-slate-900 hover:bg-emerald-600 text-white text-xs font-bold rounded-xl transition shadow-sm"
        >
          📷 Simulate Kiosk Drop Here (+1.25 kg {{ bin.rubbishTypeName }})
        </button>
        <div v-else class="text-center py-2 bg-rose-50 text-rose-600 rounded-xl text-xs font-bold">
          ⚠️ Compartment Unavailable (Full or Maintenance)
        </div>
      </div>
    </div>

    <!-- Station Support Footer -->
    <div class="bg-slate-100 rounded-2xl p-3.5 text-center text-xs text-slate-500">
      Need assistance at this kiosk? Call Station Support: <b class="text-slate-700">{{ station.supportPhone || '+60 12-345 6789' }}</b>
    </div>
  </div>
</template>
