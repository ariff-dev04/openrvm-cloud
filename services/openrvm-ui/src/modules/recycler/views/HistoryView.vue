<script setup lang="ts">
import type { UserAccount, SubmissionItem } from '../../../core/types'

defineProps<{
  user: UserAccount
  history: SubmissionItem[]
}>()

const emit = defineEmits<{ (e: 'back'): void }>()
</script>

<template>
  <div class="p-4 space-y-4">
    <div class="rounded-2xl bg-emerald-600 text-white p-5 shadow">
      <button @click="emit('back')" class="text-xs font-bold bg-emerald-700 px-2.5 py-1 rounded-lg mb-2">← Back</button>
      <h2 class="text-xl font-extrabold">My Recycling</h2>
      <p class="text-xs text-emerald-100">Your verified environmental impact</p>
      <div class="grid grid-cols-2 gap-3 mt-4">
        <div class="bg-emerald-700/60 p-3 rounded-xl">
          <p class="text-xl font-extrabold">{{ user.total_recycled_kg }} KG</p>
          <p class="text-[11px] text-emerald-200">Verified Weight</p>
        </div>
        <div class="bg-emerald-700/60 p-3 rounded-xl">
          <p class="text-xl font-extrabold">{{ user.points_balance }} Pts</p>
          <p class="text-[11px] text-emerald-200">+{{ user.pending_points }} Pending</p>
        </div>
      </div>
    </div>

    <div class="space-y-3">
      <h3 class="font-bold text-sm">Recent Activity</h3>
      <div v-for="item in history" :key="item.put_id" class="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex justify-between items-center">
        <div>
          <span class="text-xs font-bold text-emerald-700">{{ item.rubbish_type }}</span>
          <p class="text-xs font-semibold text-slate-700 mt-0.5">{{ item.station_name }} ({{ item.device_no }})</p>
          <p class="text-[11px] text-slate-400">{{ item.created_at }}</p>
        </div>
        <div class="text-right">
          <p class="font-bold text-sm text-slate-900">{{ item.submitted_weight_kg }} kg</p>
          <p class="text-xs font-bold text-emerald-600">+{{ item.points_awarded }} pts</p>
          <span :class="item.audit_status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-700' : (item.audit_status === 'REJECTED' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800')" class="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-bold">
            {{ item.audit_status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
