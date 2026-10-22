<script setup lang="ts">
import { ref, computed } from 'vue'
import { apiClient } from '../../../core/api'
import type { WithdrawalItem } from '../../../core/types'

const props = defineProps<{ withdrawals: WithdrawalItem[] }>()
const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'notify', msg: string): void
}>()

const withStatusFilter = ref<'PENDING' | 'PAID' | 'REJECTED'>('PENDING')
const withSearch = ref('')
const selectedWithdrawal = ref<WithdrawalItem | null>(null)

const filteredWithdrawals = computed(() => {
  return props.withdrawals.filter(w => {
    const matchStatus = w.status === withStatusFilter.value
    const q = withSearch.value.toLowerCase()
    const matchSearch = !q || w.phone.includes(q) || w.user_name.toLowerCase().includes(q) || w.bank_name.toLowerCase().includes(q) || w.account_no.includes(q)
    return matchStatus && matchSearch
  })
})

const handleWithdrawalAudit = async (id: number, action: 'PAID' | 'REJECTED') => {
  const res = await apiClient.auditWithdrawal(id, action)
  emit('notify', res.msg)
  selectedWithdrawal.value = null
  emit('refresh')
}
</script>

<template>
  <main class="p-6 space-y-4">
    <div class="flex flex-wrap justify-between items-center gap-3">
      <div>
        <h1 class="text-xl font-extrabold text-slate-900">Withdrawal Requests</h1>
        <p class="text-xs text-slate-500">Click any row to inspect IC Holder & Bank Account details before manual payout</p>
      </div>
      <div class="flex items-center gap-2">
        <input v-model="withSearch" type="text" placeholder="Search Name, Bank, or Acct..." class="px-3 py-1.5 border rounded-xl text-xs bg-white" />
        <div class="flex bg-slate-200 p-1 rounded-xl text-xs font-bold">
          <button v-for="st in (['PENDING', 'PAID', 'REJECTED'] as const)" :key="st" @click="withStatusFilter = st"
            :class="withStatusFilter === st ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'"
            class="px-3 py-1.5 rounded-lg transition">
            {{ st === 'PAID' ? 'Paid / History' : st }}
          </button>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase">
          <tr>
            <th class="p-3.5">Date</th><th>User</th><th>Phone</th><th>Bank & Account No</th><th>Account Holder (IC)</th><th>Amount</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="w in filteredWithdrawals" :key="w.id" @click="selectedWithdrawal = w" class="hover:bg-blue-50/50 cursor-pointer">
            <td class="p-3.5 text-slate-500">{{ w.created_at }}</td>
            <td class="font-bold text-slate-900">{{ w.user_name }}</td>
            <td class="font-mono">+60 {{ w.phone }}</td>
            <td>
              <p class="font-bold text-blue-700">{{ w.bank_name }}</p>
              <p class="font-mono text-slate-500">{{ w.account_no }}</p>
            </td>
            <td class="font-bold uppercase">{{ w.account_holder_name }}</td>
            <td>
              <p class="font-extrabold text-sm text-emerald-700">RM {{ w.amount_rm.toFixed(2) }}</p>
              <p class="text-slate-400">{{ w.amount_points }} pts</p>
            </td>
            <td>
              <span :class="w.status === 'PAID' ? 'bg-emerald-100 text-emerald-700' : (w.status === 'REJECTED' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800')" class="px-2 py-0.5 rounded font-bold">
                {{ w.status }}
              </span>
            </td>
            <td @click.stop>
              <button @click="selectedWithdrawal = w" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg">
                🔍 View & Payout
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- WITHDRAWAL BANK PAYOUT DETAILS MODAL -->
    <div v-if="selectedWithdrawal" class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div class="bg-white w-full max-w-md rounded-3xl p-6 shadow-2xl space-y-5">
        <div class="flex justify-between items-start">
          <div>
            <span class="px-2.5 py-0.5 bg-blue-100 text-blue-800 rounded-full text-[10px] font-bold uppercase">Bank Payout Verification</span>
            <h3 class="font-extrabold text-lg text-slate-900 mt-1">Withdrawal Request #{{ selectedWithdrawal.id }}</h3>
          </div>
          <button @click="selectedWithdrawal = null" class="text-slate-400 font-bold">✕</button>
        </div>

        <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-3 text-xs">
          <div class="flex justify-between">
            <span class="text-slate-400">Recycler Name & Phone:</span>
            <span class="font-bold text-slate-900">{{ selectedWithdrawal.user_name }} (+60 {{ selectedWithdrawal.phone }})</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Bank / eWallet Name:</span>
            <span class="font-extrabold text-blue-700 text-sm">{{ selectedWithdrawal.bank_name }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-slate-400">Bank Account Number:</span>
            <span class="font-mono font-extrabold text-sm bg-white px-2.5 py-1 rounded border">{{ selectedWithdrawal.account_no }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Holder Name (Per IC):</span>
            <span class="font-bold uppercase text-slate-900">{{ selectedWithdrawal.account_holder_name }}</span>
          </div>
          <div class="pt-2 border-t flex justify-between items-center">
            <span class="font-bold text-slate-600">Transfer Amount:</span>
            <span class="text-xl font-extrabold text-emerald-600">RM {{ selectedWithdrawal.amount_rm.toFixed(2) }} ({{ selectedWithdrawal.amount_points }} pts)</span>
          </div>
        </div>

        <div v-if="selectedWithdrawal.status === 'PENDING'" class="flex gap-2 text-xs font-bold">
          <button @click="handleWithdrawalAudit(selectedWithdrawal.id, 'REJECTED')" class="flex-1 py-3 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 rounded-xl">
            🚫 Reject & Refund Points
          </button>
          <button @click="handleWithdrawalAudit(selectedWithdrawal.id, 'PAID')" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow">
            ✅ Mark as Transferred (Paid)
          </button>
        </div>
        <div v-else class="text-center text-xs font-bold text-slate-500 py-2">
          Status: {{ selectedWithdrawal.status }}
        </div>
      </div>
    </div>
  </main>
</template>
