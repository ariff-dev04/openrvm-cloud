<script setup lang="ts">
import { apiClient } from '../../../core/api'

defineProps<{ machines: any[] }>()
const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'notify', msg: string): void
}>()

const handleToggleMachine = async (deviceNo: string) => {
  await apiClient.toggleMaintenance(deviceNo)
  emit('notify', `Toggled operation mode for ${deviceNo}`)
  emit('refresh')
}
</script>

<template>
  <main class="p-6 space-y-4">
    <div>
      <h1 class="text-xl font-extrabold text-slate-900">Machine Status</h1>
      <p class="text-xs text-slate-500">Real-time monitoring of 2-in-1 Dry RVM and UCO units</p>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase">
          <tr>
            <th class="p-3.5">Status & Zone</th><th>Location Details</th><th>Device ID</th><th>Bin Level (%)</th><th>Current Weight</th><th>Force Offline</th><th>Support</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="m in machines" :key="m.deviceNo">
            <td class="p-3.5">
              <span :class="m.maintenanceMode ? 'bg-amber-100 text-amber-800' : (m.status === 1 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700')" class="px-2.5 py-0.5 rounded-full font-bold">
                ● {{ m.maintenanceMode ? 'Maintenance' : (m.status === 1 ? 'Bin Full' : 'Online') }}
              </span>
              <p class="text-slate-400 mt-1">{{ m.zone }}</p>
            </td>
            <td>
              <p class="font-bold text-sm text-slate-900">{{ m.deviceName }}</p>
              <p class="text-slate-400">{{ m.address }}</p>
            </td>
            <td class="font-mono font-bold">{{ m.deviceNo }}</td>
            <td class="w-64 space-y-2 py-2">
              <div v-for="pos in m.positions" :key="pos.positionNo">
                <div class="flex justify-between text-[11px] font-semibold mb-0.5">
                  <span>{{ pos.rubbishTypeName }}</span>
                  <span>{{ Math.round((pos.currentWeight / pos.maxWeight) * 100) }}%</span>
                </div>
                <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                  <div :class="(pos.currentWeight / pos.maxWeight) >= 0.9 ? 'bg-rose-500' : 'bg-emerald-500'" class="h-full" :style="{ width: Math.min(100, (pos.currentWeight / pos.maxWeight) * 100) + '%' }"></div>
                </div>
              </div>
            </td>
            <td class="space-y-1 font-mono">
              <div v-for="pos in m.positions" :key="pos.positionNo">
                {{ pos.currentWeight }} / {{ pos.maxWeight }} kg
              </div>
            </td>
            <td>
              <button @click="handleToggleMachine(m.deviceNo)"
                :class="m.maintenanceMode ? 'bg-rose-600 text-white' : 'bg-slate-200 text-slate-800'"
                class="px-3 py-1.5 rounded-lg font-bold transition">
                {{ m.maintenanceMode ? '🔧 MAINTENANCE' : '⚡ AUTO MODE' }}
              </button>
            </td>
            <td class="font-mono text-slate-500">{{ m.supportPhone }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>
