<script setup lang="ts">
import { ref, onMounted } from 'vue'

const hostname = window.location.hostname
const isHostAdmin = hostname.startsWith('admin.') || window.location.search.includes('portal=admin')
const isStrictDomain = ref<boolean>(hostname.includes('ariff.lab'))
const activePortal = ref<'user' | 'admin'>(isHostAdmin ? 'admin' : 'user')
const loading = ref(false)
const toast = ref('')

const health = ref<any>({ status: 'checking...', synced_transactions: 0, sync_worker_runs: 0 })
const stations = ref<any[]>([])
const userData = ref<any>({ phone: '0123456789', nickname: 'Ariff_UKM', points_balance: 0, total_recycled_kg: 0, card_code: 'RFID-MY-001' })
const history = ref<any[]>([])

const fetchAll = async () => {
  try {
    const [hRes, sRes, uRes] = await Promise.all([
      fetch('/api/health').then(r => r.json()),
      fetch('/api/stations').then(r => r.json()),
      fetch('/api/user/0123456789/dashboard').then(r => r.json())
    ])
    health.value = hRes
    stations.value = sRes.units || []
    userData.value = uRes.user || userData.value
    history.value = uRes.history || []
  } catch (e) {
    console.error('API fetch error:', e)
  }
}

const simulateDrop = async (deviceNo: string, positionNo: number, weight: number, label: string) => {
  loading.value = true
  try {
    const res = await fetch('/api/simulator/drop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deviceNo, positionNo, phone: '0123456789', addedWeightKg: weight })
    })
    const data = await res.json()
    toast.value = `Recycled ${weight}kg of ${label}! (${data.deltaCalculation})`
    await fetchAll()
    setTimeout(() => { toast.value = '' }, 5000)
  } finally {
    loading.value = false
  }
}

const auditSubmission = async (putId: number, action: string) => {
  let corrected: number | null = null
  if (action === 'CORRECTED') {
    const input = prompt('Enter verified warehouse weight (kg):', '1.0')
    if (!input) return
    corrected = parseFloat(input)
  }
  await fetch(`/api/admin/audit/${putId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, corrected_weight_kg: corrected })
  })
  toast.value = `Audit updated: #${putId} -> ${action}`
  await fetchAll()
  setTimeout(() => { toast.value = '' }, 4000)
}

onMounted(() => {
  fetchAll()
  setInterval(fetchAll, 8000)
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 pb-12">
    <header class="border-b border-slate-800 bg-slate-900/90 sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-bold text-xs border border-emerald-500/30">OpenRVM v2.0</span>
          <h1 class="font-bold text-lg">
             {{ activePortal === 'admin' ? '🖥️ Merchant Admin & Audit Platform' : '📱 Smart Recycler User App' }}
            </h1>
        </div>
        <div v-if="!isStrictDomain" class="flex items-center gap-2 bg-slate-800 p-1 rounded-lg">
          <button @click="activePortal = 'user'" :class="activePortal === 'user' ? 'bg-emerald-600 text-white' : 'text-slate-400'" class="px-3 py-1.5 rounded-md text-sm font-medium transition">
            📱 User Recycler App
          </button>
          <button @click="activePortal = 'admin'" :class="activePortal === 'admin' ? 'bg-indigo-600 text-white' : 'text-slate-400'" class="px-3 py-1.5 rounded-md text-sm font-medium transition">
            🖥️ Merchant Admin Platform
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 mt-6">
      <div v-if="toast" class="mb-6 p-4 rounded-xl bg-emerald-900/60 border border-emerald-500 text-emerald-200 text-sm font-medium">
        ✅ {{ toast }}
      </div>

      <!-- USER RECYCLER PORTAL -->
      <div v-if="activePortal === 'user'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <p class="text-xs text-slate-400 uppercase">Recycler Account</p>
            <p class="text-xl font-bold mt-1">{{ userData.nickname }} ({{ userData.phone }})</p>
            <p class="text-xs text-emerald-400 mt-1">Bound Card: {{ userData.card_code }}</p>
          </div>
          <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <p class="text-xs text-slate-400 uppercase">Eco-Points Balance</p>
            <p class="text-3xl font-extrabold text-emerald-400 mt-1">{{ userData.points_balance }} pts</p>
            <p class="text-xs text-slate-500 mt-1">Est. Value: RM {{ (userData.points_balance * 0.1).toFixed(2) }}</p>
          </div>
          <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <p class="text-xs text-slate-400 uppercase">Lifetime Recycled Weight</p>
            <p class="text-3xl font-extrabold text-sky-400 mt-1">{{ userData.total_recycled_kg }} kg</p>
            <p class="text-xs text-slate-500 mt-1">Dry RVM + UCO Cooking Oil</p>
          </div>
        </div>

        <!-- 2-in-1 Station Live Status & Simulator Buttons -->
        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <h2 class="text-base font-bold mb-4">📍 Nearby 2-in-1 Station: UKM Bangi EcoHub (Live Hardware Telemetry)</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="unit in stations" :key="unit.deviceNo" class="border border-slate-800 bg-slate-950 p-4 rounded-lg">
              <div class="flex justify-between items-center mb-3">
                <span class="font-semibold text-sm">{{ unit.deviceType === 'DRY_2BIN' ? '♻️ 2-Door Dry RVM' : '🛢️ UCO Cooking Oil Unit' }}</span>
                <span class="text-xs px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded">ID: {{ unit.deviceNo }}</span>
              </div>
              <div v-for="bin in unit.compartments" :key="bin.positionNo" class="mb-3 p-3 bg-slate-900 rounded border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1">
                  <span class="font-medium">Bin #{{ bin.positionNo }}: {{ bin.rubbishTypeName }} ({{ bin.integral }} pts/kg)</span>
                  <span class="text-slate-400">{{ bin.currentWeight }} / {{ bin.maxWeight }} kg</span>
                </div>
                <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden mb-2">
                  <div class="bg-emerald-500 h-full" :style="{ width: Math.min(100, (bin.currentWeight / bin.maxWeight) * 100) + '%' }"></div>
                </div>
                <button :disabled="loading" @click="simulateDrop(unit.deviceNo, bin.positionNo, 1.2, bin.rubbishTypeName)" class="w-full py-1.5 bg-emerald-600 hover:bg-emerald-500 text-xs font-bold rounded text-white transition">
                  + Simulate Drop (+1.2 kg {{ bin.rubbishTypeName }})
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- User Recycling Logs -->
        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <h2 class="text-base font-bold mb-3">📜 My Recycling Transactions</h2>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="text-xs text-slate-400 border-b border-slate-800">
                <tr><th class="py-2">Put ID</th><th>Item</th><th>Weight</th><th>Points</th><th>Audit Status</th><th>Time</th></tr>
              </thead>
              <tbody class="divide-y divide-slate-800">
                <tr v-for="item in history" :key="item.put_id">
                  <td class="py-2.5 font-mono text-xs">#{{ item.put_id }}</td>
                  <td>{{ item.rubbish_type }}</td>
                  <td>{{ item.submitted_weight_kg }} kg</td>
                  <td class="text-emerald-400 font-bold">+{{ item.points_awarded }}</td>
                  <td><span class="px-2 py-0.5 text-xs rounded bg-slate-800">{{ item.audit_status }}</span></td>
                  <td class="text-xs text-slate-400">{{ item.created_at }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- MERCHANT ADMIN PLATFORM -->
      <div v-else class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <p class="text-xs text-slate-400">FastAPI Sync Status</p>
            <p class="text-xl font-bold text-emerald-400 mt-1">{{ health.status }}</p>
          </div>
          <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <p class="text-xs text-slate-400">Redis Idempotent Sync Runs</p>
            <p class="text-xl font-bold text-indigo-400 mt-1">{{ health.sync_worker_runs }} cycles</p>
          </div>
          <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <p class="text-xs text-slate-400">Total Reconciled Logs</p>
            <p class="text-xl font-bold text-sky-400 mt-1">{{ health.synced_transactions }} records</p>
          </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <h2 class="text-base font-bold mb-3">⚖️ Merchant Weight Reconciliation & Fraud Audit</h2>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="text-xs text-slate-400 border-b border-slate-800">
                <tr><th class="py-2">Put ID</th><th>Device ID</th><th>Type</th><th>User Weight</th><th>Bin Total</th><th>Points</th><th>Status</th><th>Audit Action</th></tr>
              </thead>
              <tbody class="divide-y divide-slate-800">
                <tr v-for="item in history" :key="item.put_id">
                  <td class="py-2.5 font-mono text-xs">#{{ item.put_id }}</td>
                  <td class="font-mono text-xs">{{ item.device_no }}</td>
                  <td>{{ item.rubbish_type }}</td>
                  <td>{{ item.submitted_weight_kg }} kg</td>
                  <td>{{ item.bin_position_weight_kg }} kg</td>
                  <td class="text-emerald-400 font-bold">{{ item.points_awarded }}</td>
                  <td><span class="px-2 py-0.5 text-xs rounded bg-slate-800">{{ item.audit_status }}</span></td>
                  <td class="space-x-1">
                    <button @click="auditSubmission(item.put_id, 'ACCEPTED')" class="px-2 py-1 bg-emerald-600 text-xs rounded">Accept</button>
                    <button @click="auditSubmission(item.put_id, 'CORRECTED')" class="px-2 py-1 bg-amber-600 text-xs rounded">Correct</button>
                    <button @click="auditSubmission(item.put_id, 'REJECTED')" class="px-2 py-1 bg-rose-600 text-xs rounded">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
