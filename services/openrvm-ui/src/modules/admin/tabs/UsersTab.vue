<script setup lang="ts">
import { ref, computed } from 'vue'
import type { UserAccount } from '../../../core/types'

const props = defineProps<{ users: UserAccount[] }>()
const search = ref('')

const filteredUsers = computed(() => {
  const q = search.value.toLowerCase()
  return props.users.filter(u =>
    !q || u.nickname.toLowerCase().includes(q) || u.phone.includes(q) || (u.card_code || '').toLowerCase().includes(q)
  )
})
</script>

<template>
  <main class="p-6 space-y-4">
    <div class="flex flex-wrap justify-between items-center gap-3">
      <div>
        <h1 class="text-xl font-extrabold text-slate-900">Registered Recyclers (User CRM)</h1>
        <p class="text-xs text-slate-500">View recycler profiles, RFID card bindings, pending escrow points, and approved balances</p>
      </div>
      <input v-model="search" type="text" placeholder="Search Name, Phone, or RFID Card..." class="px-3.5 py-2 border border-slate-300 rounded-xl text-xs w-64 bg-white" />
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase">
          <tr>
            <th class="p-3.5">User ID</th><th>Recycler Profile</th><th>Phone (Hardware ID)</th><th>RFID Card</th><th>Total Recycled</th><th>Pending Escrow</th><th>Approved Balance</th><th>Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="u in filteredUsers" :key="u.id" class="hover:bg-slate-50">
            <td class="p-3.5 font-mono font-bold text-slate-500">#USR-{{ u.id }}</td>
            <td class="flex items-center gap-2.5 py-3">
              <div class="w-8 h-8 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center">
                {{ u.nickname.charAt(0) }}
              </div>
              <div>
                <p class="font-bold text-slate-900">{{ u.nickname }}</p>
                <p class="text-[11px] text-slate-400">{{ u.google_email || 'OTP Verified User' }}</p>
              </div>
            </td>
            <td class="font-mono font-bold">+60 {{ u.phone }}</td>
            <td><span class="px-2 py-0.5 bg-slate-100 border rounded font-mono text-[11px]">{{ u.card_code || 'Unbound' }}</span></td>
            <td class="font-bold text-sky-700">{{ u.total_recycled_kg }} kg</td>
            <td>
              <span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full font-bold">+{{ u.pending_points }} pts</span>
            </td>
            <td>
              <p class="font-extrabold text-emerald-700 text-sm">{{ u.points_balance }} pts</p>
              <p class="text-[10px] text-slate-400">RM {{ (u.points_balance / 100).toFixed(2) }}</p>
            </td>
            <td>
              <span :class="u.is_verified ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'" class="px-2 py-0.5 rounded-full font-bold text-[10px]">
                {{ u.is_verified ? '● Verified' : 'Unverified' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>
