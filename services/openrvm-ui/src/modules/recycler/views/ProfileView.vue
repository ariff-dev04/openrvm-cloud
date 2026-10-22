<script setup lang="ts">
import type { UserAccount } from '../../../core/types'

defineProps<{ user: UserAccount }>()
const emit = defineEmits<{
  (e: 'logout'): void
  (e: 'delete-account'): void
}>()
</script>

<template>
  <div class="p-4 space-y-5">
    <div class="rounded-2xl bg-emerald-600 text-white p-6 text-center shadow">
      <div class="w-16 h-16 mx-auto rounded-full bg-white text-emerald-700 font-extrabold text-2xl flex items-center justify-center shadow">
        {{ user.nickname.charAt(0) }}
      </div>
      <h2 class="text-lg font-bold mt-2">{{ user.nickname }}</h2>
      <p class="text-xs text-emerald-100">{{ user.google_email || 'Verified Recycler' }}</p>
      <p class="text-xs text-emerald-200 mt-0.5">Phone: +60 {{ user.phone }} | Card: {{ user.card_code }}</p>
    </div>

    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 grid grid-cols-2 gap-3 text-center">
      <div class="p-3 bg-slate-50 rounded-xl">
        <p class="text-xs text-slate-400">Total Recycled</p>
        <p class="text-lg font-extrabold text-slate-900">{{ user.total_recycled_kg }} kg</p>
      </div>
      <div class="p-3 bg-slate-50 rounded-xl">
        <p class="text-xs text-slate-400">Approved Points</p>
        <p class="text-lg font-extrabold text-emerald-600">{{ user.points_balance }} pts</p>
      </div>
    </div>

    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 space-y-3">
      <button @click="emit('logout')" class="w-full py-3 bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold rounded-xl text-sm transition">
        Switch Account / Logout
      </button>
      <button @click="emit('delete-account')" class="w-full py-3 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 font-bold rounded-xl text-sm transition">
        🗑️ Delete My Account & Data (PDPA)
      </button>
    </div>
  </div>
</template>
