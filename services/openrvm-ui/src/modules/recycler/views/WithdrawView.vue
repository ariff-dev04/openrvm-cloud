<script setup lang="ts">
import { ref } from 'vue'
import type { UserAccount, WithdrawalItem } from '../../../core/types'

defineProps<{
  user: UserAccount
  withdrawals: WithdrawalItem[]
}>()

const emit = defineEmits<{
  (e: 'back'): void
  (e: 'submit', payload: { amount_points: number; bank_name: string; account_no: string; account_holder_name: string }): void
}>()

const withdrawPoints = ref<number>(500)
const bankName = ref<string>('Maybank')
const accountNo = ref<string>('')
const accountHolder = ref<string>('')

const onSubmit = () => {
  emit('submit', {
    amount_points: Number(withdrawPoints.value),
    bank_name: bankName.value,
    account_no: accountNo.value,
    account_holder_name: accountHolder.value
  })
  accountNo.value = ''
}
</script>

<template>
  <div class="p-4 space-y-5">
    <div class="flex items-center gap-3">
      <button @click="emit('back')" class="px-3 py-1.5 bg-white border rounded-xl text-sm font-bold">← Back</button>
      <h2 class="font-bold text-lg">Withdraw Points</h2>
    </div>

    <div class="rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-5 shadow-lg">
      <p class="text-xs text-blue-100">Available to Withdraw</p>
      <p class="text-3xl font-extrabold mt-1">RM {{ (user.points_balance / 100).toFixed(2) }}</p>
      <p class="text-xs text-blue-200 mt-1">{{ user.points_balance }} Approved Points (Pending: {{ user.pending_points }} pts)</p>
    </div>

    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 space-y-3">
      <h3 class="font-bold text-sm">Request Bank Withdrawal</h3>
      <div>
        <label class="text-xs font-semibold text-slate-600">Amount (Points to withdraw — 100 pts = RM 1.00)</label>
        <input v-model="withdrawPoints" type="number" step="100" min="500" class="w-full mt-1 px-3 py-2.5 border rounded-xl text-sm" />
        <p class="text-[11px] text-slate-400 mt-1">Min: RM 5.00 (500 pts) | Max: RM 200.00 | Conversion: RM {{ (withdrawPoints / 100).toFixed(2) }}</p>
      </div>
      <div>
        <label class="text-xs font-semibold text-slate-600">Bank Name</label>
        <select v-model="bankName" class="w-full mt-1 px-3 py-2.5 border rounded-xl text-sm bg-white">
          <option>Maybank</option>
          <option>CIMB Bank</option>
          <option>Touch 'n Go eWallet</option>
          <option>Bank Islam</option>
          <option>Public Bank</option>
          <option>RHB Bank</option>
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold text-slate-600">Account No.</label>
        <input v-model="accountNo" type="text" placeholder="e.g. 162012998877" class="w-full mt-1 px-3 py-2.5 border rounded-xl text-sm font-mono" />
      </div>
      <div>
        <label class="text-xs font-semibold text-slate-600">Account Holder Name (Full Name per IC)</label>
        <input v-model="accountHolder" type="text" placeholder="MUHAMMAD ARIFF BIN MOHD ZAKARIA" class="w-full mt-1 px-3 py-2.5 border rounded-xl text-sm uppercase" />
      </div>
      <button @click="onSubmit" class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow transition">
        Submit Request
      </button>
    </div>

    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 space-y-2">
      <h3 class="font-bold text-sm">Withdrawal History</h3>
      <div v-for="w in withdrawals" :key="w.id" class="flex justify-between items-center py-2 border-b last:border-0 text-xs">
        <div>
          <p class="font-bold">{{ w.bank_name }} ({{ w.account_no }})</p>
          <p class="text-slate-400">{{ w.created_at }}</p>
        </div>
        <div class="text-right">
          <p class="font-bold text-slate-900">RM {{ w.amount_rm.toFixed(2) }}</p>
          <span :class="w.status === 'PAID' ? 'bg-emerald-100 text-emerald-700' : (w.status === 'REJECTED' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700')" class="px-2 py-0.5 rounded text-[10px] font-bold">
            {{ w.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
