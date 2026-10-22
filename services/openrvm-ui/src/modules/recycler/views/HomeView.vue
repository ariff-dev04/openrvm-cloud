<script setup lang="ts">
import type { UserAccount, StationGroup } from '../../../core/types'

defineProps<{
  user: UserAccount
  stations: StationGroup[]
}>()

const emit = defineEmits<{
  (e: 'navigate', screen: 'withdraw' | 'history'): void
  (e: 'select-station', station: StationGroup): void
}>()
</script>

<template>
  <div class="p-4 space-y-5">
    <!-- Top User Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-11 h-11 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-lg shadow">
          {{ user.nickname.charAt(0) }}
        </div>
        <div>
          <p class="font-bold text-sm text-slate-900">Hello, {{ user.nickname }}</p>
          <p class="text-xs text-slate-500">Ready to recycle today?</p>
        </div>
      </div>
      <span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">EN</span>
    </div>

    <!-- Promo Banner -->
    <div class="rounded-2xl bg-gradient-to-r from-emerald-700 to-teal-600 text-white p-5 shadow-md">
      <p class="text-xs uppercase tracking-wider font-semibold text-emerald-200">Rakyat Eco Initiative</p>
      <h2 class="text-xl font-extrabold mt-1">SAVE THE EARTH 🌍</h2>
      <p class="text-xs text-emerald-100 mt-1">Recycle Plastic, Cans, Paper & Used Cooking Oil (UCO) at 2-in-1 Stations.</p>
    </div>

    <!-- Dual Impact Card -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 grid grid-cols-2 divide-x divide-slate-200">
      <button @click="emit('navigate', 'history')" class="pr-3 text-left hover:bg-slate-50 rounded-l-xl transition">
        <div class="flex items-center gap-2 text-emerald-600 text-xs font-bold">
          <span>⚖️</span><span>DELIVERED WEIGHT</span>
        </div>
        <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ user.total_recycled_kg }}<span class="text-sm font-normal"> kg</span></p>
        <p class="text-[11px] text-emerald-600 font-medium mt-1">View History →</p>
      </button>

      <button @click="emit('navigate', 'withdraw')" class="pl-4 text-left hover:bg-slate-50 rounded-r-xl transition">
        <div class="flex items-center gap-2 text-amber-600 text-xs font-bold">
          <span>🪙</span><span>BALANCE</span>
        </div>
        <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ user.points_balance }}<span class="text-sm font-normal"> pts</span></p>
        <span v-if="user.pending_points > 0" class="inline-block mt-1 px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-[11px] font-bold">
          +{{ user.pending_points }} pending
        </span>
        <p v-else class="text-[11px] text-blue-600 font-medium mt-1">Withdraw RM →</p>
      </button>
    </div>

    <!-- Nearby Stations Section -->
    <div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-bold text-sm text-slate-800">📍 Nearby Stations (Tap for Maps & Details)</h3>
        <span class="text-xs text-emerald-600 font-semibold">{{ stations.length }} Active Hubs</span>
      </div>

      <div class="space-y-4">
        <div
          v-for="st in stations"
          :key="st.stationName"
          @click="emit('select-station', st)"
          class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 space-y-3 cursor-pointer hover:border-emerald-500 hover:shadow-md transition"
        >
          <div class="flex justify-between items-start">
            <div>
              <span :class="st.isOnline ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                ● {{ st.isOnline ? 'Online' : 'Maintenance' }}
              </span>
              <h4 class="font-bold text-base text-slate-900 mt-1">{{ st.stationName }}</h4>
              <p class="text-xs text-slate-500">{{ st.address }}</p>
            </div>
            <div class="text-right">
              <span class="text-xs font-bold text-slate-600">{{ st.distanceKm }} km</span>
              <div class="mt-1 px-2.5 py-1 bg-emerald-600 text-white text-xs font-bold rounded-lg shadow-sm">
                GO ↗
              </div>
            </div>
          </div>

          <div class="space-y-2 pt-2 border-t border-slate-100">
            <div v-for="bin in st.bins" :key="bin.deviceNo + '-' + bin.positionNo" class="text-xs">
              <div class="flex justify-between mb-1">
                <span class="font-semibold text-slate-700">{{ bin.rubbishTypeName }}</span>
                <span :class="bin.fillPercent >= 80 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold'">
                  {{ bin.statusLabel }} ({{ bin.fillPercent }}%)
                </span>
              </div>
              <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                <div
                  :class="bin.fillPercent >= 95 ? 'bg-rose-500' : (bin.fillPercent >= 80 ? 'bg-amber-500' : 'bg-emerald-500')"
                  class="h-full transition-all"
                  :style="{ width: bin.fillPercent + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
