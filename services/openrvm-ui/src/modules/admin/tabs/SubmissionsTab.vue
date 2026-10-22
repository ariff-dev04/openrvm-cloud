<script setup lang="ts">
import { ref, computed } from 'vue'
import { apiClient } from '../../../core/api'
import type { SubmissionItem } from '../../../core/types'

const props = defineProps<{ submissions: SubmissionItem[] }>()
const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'notify', msg: string): void
}>()

const subStatusFilter = ref<'PENDING' | 'VERIFIED' | 'REJECTED'>('PENDING')
const subSearch = ref('')
const subWasteType = ref('ALL')

const selectedSub = ref<SubmissionItem | null>(null)
const actualWeightInput = ref<number>(1.25)

const filteredSubmissions = computed(() => {
  return props.submissions.filter(s => {
    const matchStatus = s.audit_status === subStatusFilter.value
    const matchType = subWasteType.value === 'ALL' || s.rubbish_type === subWasteType.value
    const q = subSearch.value.toLowerCase()
    const matchSearch = !q || s.phone.includes(q) || s.device_no.toLowerCase().includes(q) || String(s.put_id).includes(q) || s.user_name.toLowerCase().includes(q)
    return matchStatus && matchType && matchSearch
  })
})

const openCorrectModal = (sub: SubmissionItem) => {
  selectedSub.value = sub
  actualWeightInput.value = sub.submitted_weight_kg
}

const parsedSnapshots = computed(() => {
  if (!selectedSub.value?.snapshot_urls) return null
  const parts = selectedSub.value.snapshot_urls.split(',')
  return { before: parts[0] || '', after: parts[1] || parts[0] || '' }
})

const calculatedModalPoints = computed(() => {
  if (!selectedSub.value) return '0.00'
  return (Number(actualWeightInput.value || 0) * selectedSub.value.rate_per_kg).toFixed(2)
})

const handleQuickAudit = async (putId: number, action: 'VERIFIED' | 'REJECTED') => {
  const res = await apiClient.auditSubmission(putId, action)
  emit('notify', res.msg)
  selectedSub.value = null
  emit('refresh')
}

const handleConfirmCorrection = async () => {
  if (!selectedSub.value) return
  const res = await apiClient.auditSubmission(selectedSub.value.put_id, 'CORRECTED', Number(actualWeightInput.value))
  emit('notify', res.msg)
  selectedSub.value = null
  emit('refresh')
}

const handleForceSync = async () => {
  const res = await apiClient.forceSync()
  emit('notify', res.msg)
  emit('refresh')
}
</script>

<template>
  <main class="p-6 space-y-4">
    <div class="flex flex-wrap justify-between items-center gap-3">
      <div>
        <h1 class="text-xl font-extrabold text-slate-900">Submission Verification</h1>
        <p class="text-xs text-slate-500">Verify user recycling claims and audit Before/After bin camera snapshots</p>
      </div>
      <button @click="handleForceSync" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow transition">
        ⚡ Force Sync Vendor API
      </button>
    </div>

    <!-- Filter Bar & Status Tabs -->
    <div class="bg-white p-3 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2">
        <input v-model="subSearch" type="text" placeholder="Search Phone, Machine No, or ID..." class="px-3 py-1.5 border rounded-xl text-xs w-64" />
        <select v-model="subWasteType" class="px-3 py-1.5 border rounded-xl text-xs bg-white">
          <option value="ALL">All Waste Types</option>
          <option value="Plastic & Can">Plastic & Can</option>
          <option value="Paper">Paper</option>
          <option value="Used Cooking Oil">Used Cooking Oil</option>
        </select>
      </div>
      <div class="flex bg-slate-100 p-1 rounded-xl text-xs font-bold">
        <button v-for="st in (['PENDING', 'VERIFIED', 'REJECTED'] as const)" :key="st" @click="subStatusFilter = st"
          :class="subStatusFilter === st ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'"
          class="px-3 py-1.5 rounded-lg transition">
          {{ st }}
        </button>
      </div>
    </div>

    <!-- Verification Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase">
          <tr>
            <th class="p-3.5">Submitted At</th><th>User</th><th>ID</th><th>Machine</th><th>Type</th><th>Photos</th><th>User Wgt</th><th>Bin Lvl</th><th>Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="s in filteredSubmissions" :key="s.put_id" class="hover:bg-slate-50">
            <td class="p-3.5 text-slate-500">{{ s.created_at }}</td>
            <td>
              <p class="font-bold text-slate-900">{{ s.user_name }}</p>
              <p class="text-slate-400 font-mono">+60 {{ s.phone }}</p>
            </td>
            <td class="font-mono font-bold text-slate-600">#{{ s.put_id }}</td>
            <td>
              <p class="font-bold">{{ s.device_no }}</p>
              <p class="text-slate-400">{{ s.station_name }}</p>
            </td>
            <td>
              <span :class="s.device_type === 'UCO_OIL' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'" class="px-2 py-0.5 rounded-full font-bold">
                {{ s.rubbish_type }}
              </span>
            </td>
            <td>
              <button v-if="s.snapshot_urls" @click="openCorrectModal(s)" class="px-2.5 py-1 bg-slate-800 text-white rounded-lg font-semibold hover:bg-slate-700">
                📷 View 2 Photos
              </button>
              <span v-else class="text-amber-700 font-semibold">🛢️ Fluid Sensor OK</span>
            </td>
            <td class="font-bold text-slate-900">{{ s.submitted_weight_kg }} kg</td>
            <td class="text-slate-600">{{ s.bin_position_weight_kg }} kg</td>
            <td class="space-x-1.5">
              <button @click="handleQuickAudit(s.put_id, 'VERIFIED')" title="Instant Approve" class="px-2.5 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg">✓</button>
              <button @click="openCorrectModal(s)" title="Inspect Photos & Correct Weight" class="px-2.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg">✏️</button>
              <button @click="handleQuickAudit(s.put_id, 'REJECTED')" title="Reject" class="px-2.5 py-1.5 bg-rose-500 hover:bg-rose-600 text-white font-bold rounded-lg">✕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- SPLIT-SCREEN "CORRECT SUBMISSION" CAMERA SNAPSHOT MODAL -->
    <div v-if="selectedSub" class="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4">
      <div class="bg-white w-full max-w-4xl rounded-3xl overflow-hidden shadow-2xl grid grid-cols-1 md:grid-cols-12">
        <div class="md:col-span-7 bg-slate-950 p-5 space-y-4 flex flex-col justify-center">
          <template v-if="parsedSnapshots">
            <div class="relative rounded-2xl overflow-hidden border border-slate-800">
              <span class="absolute top-3 left-3 px-2.5 py-1 bg-amber-500 text-slate-950 font-extrabold text-[10px] rounded-md uppercase">
                BEFORE (BIN STATE: {{ selectedSub.prev_bin_weight_kg }} KG)
              </span>
              <img :src="parsedSnapshots.before" alt="Before Snapshot" class="w-full h-48 object-cover" />
            </div>
            <div class="relative rounded-2xl overflow-hidden border border-slate-800">
              <span class="absolute top-3 left-3 px-2.5 py-1 bg-sky-500 text-slate-950 font-extrabold text-[10px] rounded-md uppercase">
                AFTER (SUBMISSION: {{ selectedSub.bin_position_weight_kg }} KG)
              </span>
              <img :src="parsedSnapshots.after" alt="After Snapshot" class="w-full h-48 object-cover" />
            </div>
          </template>
          <div v-else class="text-center text-slate-300 py-16 space-y-2">
            <p class="text-4xl">🛢️</p>
            <p class="font-bold text-base">Used Cooking Oil (UCO) Fluid Sensor Verified</p>
            <p class="text-xs text-slate-400">No camera snapshot needed — Capacitance sensor verified zero water/impurity contamination.</p>
          </div>
        </div>

        <div class="md:col-span-5 p-6 flex flex-col justify-between space-y-5">
          <div class="space-y-4">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-extrabold text-lg text-slate-900">Correct Submission</h3>
                <p class="text-xs font-mono text-slate-400"># REC-{{ selectedSub.put_id }}</p>
              </div>
              <button @click="selectedSub = null" class="text-slate-400 hover:text-slate-700 font-bold">✕</button>
            </div>

            <div class="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
              <div>
                <p class="text-slate-400 font-semibold">WASTE TYPE</p>
                <p class="font-bold text-slate-900 mt-0.5">{{ selectedSub.rubbish_type }}</p>
              </div>
              <div>
                <p class="text-slate-400 font-semibold">RATE</p>
                <p class="font-bold text-emerald-600 mt-0.5">{{ selectedSub.rate_per_kg }} pts / kg</p>
              </div>
            </div>

            <div>
              <label class="text-xs font-bold text-slate-700">⚖️ Actual Delivery Weight (KG)</label>
              <input v-model="actualWeightInput" type="number" step="0.05" class="w-full mt-1 px-3.5 py-2.5 border-2 border-blue-500 rounded-xl font-extrabold text-base outline-none" />
              <p class="text-[11px] text-slate-400 mt-1">Machine Delta: {{ selectedSub.submitted_weight_kg }} kg (Bin: {{ selectedSub.prev_bin_weight_kg }}kg → {{ selectedSub.bin_position_weight_kg }}kg)</p>
            </div>

            <div class="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex justify-between items-center">
              <span class="text-xs font-bold text-amber-900">🧮 Points Awarded</span>
              <span class="text-2xl font-extrabold text-amber-600">{{ calculatedModalPoints }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between gap-2 pt-4 border-t border-slate-200 text-xs font-bold">
            <button @click="handleQuickAudit(selectedSub.put_id, 'REJECTED')" class="px-3.5 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl">
              🚫 Reject
            </button>
            <div class="flex gap-2">
              <button @click="selectedSub = null" class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl">
                Cancel
              </button>
              <button @click="handleConfirmCorrection" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow">
                Confirm & Approve
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
