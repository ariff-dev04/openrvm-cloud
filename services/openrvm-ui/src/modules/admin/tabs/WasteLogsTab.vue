<script setup lang="ts">
defineProps<{ logs: any[] }>()
</script>

<template>
  <main class="p-6 space-y-4">
    <div>
      <h1 class="text-xl font-extrabold text-slate-900">Collector Waste & Bin Cleaning Logs</h1>
      <p class="text-xs text-slate-500">Audit trail of physical RVM bin emptying and UCO tank collection by logistics teams</p>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase">
          <tr>
            <th class="p-3.5">Log ID</th><th>Device ID</th><th>Station Location</th><th>Collector / Logistics Team</th><th>Collected Weight</th><th>Timestamp</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="c in logs" :key="c.id" class="hover:bg-slate-50">
            <td class="p-3.5 font-mono font-bold text-slate-500">#CLN-{{ c.id }}</td>
            <td class="font-mono font-bold">{{ c.device_no }}</td>
            <td class="font-bold text-slate-900">{{ c.station_name }}</td>
            <td>{{ c.collector_name }}</td>
            <td class="font-extrabold text-emerald-700">{{ c.collected_weight_kg }} kg</td>
            <td class="text-slate-500">{{ c.cleaned_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>
