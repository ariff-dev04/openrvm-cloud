<script setup lang="ts">
import type { SubmissionItem, WithdrawalItem } from '../../../core/types'

defineProps<{
  kpis: {
    pendingWithdrawals: number
    onlineMachines: string
    totalPoints: number
    recycledWeightKg: number
  }
  submissions: SubmissionItem[]
  cleaningLogs: any[]
  withdrawals: WithdrawalItem[]
}>()

const emit = defineEmits<{
  (e: 'navigate', tab: 'submissions' | 'withdrawals' | 'machines' | 'logs'): void
}>()
</script>

<template>
  <main class="p-6 space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-xl font-extrabold text-slate-900">Dashboard</h1>
        <p class="text-xs text-slate-500">Overview of system performance and recycling activity</p>
      </div>
      <button @click="emit('navigate', 'machines')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow transition">
        📊 Open Big Data Telemetry
      </button>
    </div>

    <!-- 4 KPI Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div @click="emit('navigate', 'withdrawals')" class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm cursor-pointer hover:border-amber-400 transition">
        <div class="flex justify-between text-xs text-slate-400 font-semibold"><span>Pending Withdrawals</span><span>🟠</span></div>
        <p class="text-2xl font-extrabold text-slate-900 mt-2">{{ kpis.pendingWithdrawals }}</p>
        <p class="text-[11px] text-amber-600 font-bold mt-1">Action Required →</p>
      </div>
      <div @click="emit('navigate', 'machines')" class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm cursor-pointer hover:border-emerald-400 transition">
        <div class="flex justify-between text-xs text-slate-400 font-semibold"><span>Online Machines</span><span>🟢</span></div>
        <p class="text-2xl font-extrabold text-slate-900 mt-2">{{ kpis.onlineMachines }}</p>
        <p class="text-[11px] text-emerald-600 font-bold mt-1">Active Units →</p>
      </div>
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex justify-between text-xs text-slate-400 font-semibold"><span>Total Approved Points</span><span>🔵</span></div>
        <p class="text-2xl font-extrabold text-slate-900 mt-2">{{ kpis.totalPoints }} pts</p>
        <p class="text-[11px] text-blue-600 font-bold mt-1">Lifetime Value</p>
      </div>
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex justify-between text-xs text-slate-400 font-semibold"><span>Verified Recycled Weight</span><span>🟣</span></div>
        <p class="text-2xl font-extrabold text-slate-900 mt-2">{{ kpis.recycledWeightKg }} kg</p>
        <p class="text-[11px] text-purple-600 font-bold mt-1">Environmental Impact</p>
      </div>
    </div>

    <!-- 3 Live Activity Panels -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-bold text-sm">♻️ Live Recycling</h3>
          <button @click="emit('navigate', 'submissions')" class="text-xs text-blue-600 font-bold hover:underline">View All</button>
        </div>
        <div class="space-y-2.5 text-xs">
          <div v-for="s in submissions.slice(0, 4)" :key="s.put_id" class="flex justify-between items-center py-1.5 border-b last:border-0">
            <div>
              <p class="font-bold text-slate-800">{{ s.user_name }} ({{ s.rubbish_type }})</p>
              <p class="text-slate-400 text-[11px]">{{ s.station_name }} • {{ s.created_at }}</p>
            </div>
            <span :class="s.audit_status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-800'" class="px-2 py-0.5 rounded font-bold text-[10px]">
              {{ s.submitted_weight_kg }}kg ({{ s.audit_status }})
            </span>
          </div>
        </div>
      </div>

      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-bold text-sm">🚛 Collector Cleaning Logs</h3>
          <button @click="emit('navigate', 'logs')" class="text-xs text-blue-600 font-bold hover:underline">View All</button>
        </div>
        <div class="space-y-2.5 text-xs">
          <div v-for="c in cleaningLogs" :key="c.id" class="flex justify-between items-center py-1.5 border-b last:border-0">
            <div>
              <p class="font-bold text-slate-800">{{ c.station_name }} ({{ c.device_no }})</p>
              <p class="text-slate-400 text-[11px]">{{ c.collector_name }} • {{ c.cleaned_at }}</p>
            </div>
            <span class="font-bold text-emerald-700">{{ c.collected_weight_kg }} kg</span>
          </div>
        </div>
      </div>

      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-bold text-sm">💸 Recent Withdrawals</h3>
          <button @click="emit('navigate', 'withdrawals')" class="text-xs text-blue-600 font-bold hover:underline">View All</button>
        </div>
        <div class="space-y-2.5 text-xs">
          <div v-for="w in withdrawals.slice(0, 4)" :key="w.id" class="flex justify-between items-center py-1.5 border-b last:border-0">
            <div>
              <p class="font-bold text-slate-800">{{ w.user_name }} ({{ w.bank_name }})</p>
              <p class="text-slate-400 text-[11px]">{{ w.account_no }}</p>
            </div>
            <span :class="w.status === 'PAID' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-800'" class="px-2 py-0.5 rounded font-bold text-[10px]">
              RM {{ w.amount_rm.toFixed(2) }} ({{ w.status }})
            </span>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
