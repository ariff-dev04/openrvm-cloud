<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { apiClient } from '../../core/api'
import type { UserAccount, StationGroup, SubmissionItem, WithdrawalItem } from '../../core/types'
import StationDetailView from './StationDetailView.vue'

const selectedStation = ref<StationGroup | null>(null)
const props = defineProps<{ phone: string }>()
const emit = defineEmits<{ (e: 'logout'): void }>()

const activeScreen = ref<'home' | 'withdraw' | 'history' | 'profile'>('home')
const showQrModal = ref(false)
const toast = ref('')
const errorToast = ref('')
const loading = ref(false)

const user = ref<UserAccount>({
  id: 1, phone: props.phone, nickname: 'Ariff Bin Zakaria',
  points_balance: 1500, pending_points: 62.5, total_recycled_kg: 12.5, is_verified: true
})
const stations = ref<StationGroup[]>([])
const history = ref<SubmissionItem[]>([])
const withdrawals = ref<WithdrawalItem[]>([])

// Withdraw Form State (Matching Withdraw Screenshot!)
const withdrawPoints = ref<number>(500)
const bankName = ref<string>('Maybank')
const accountNo = ref<string>('')
const accountHolder = ref<string>('')

const loadData = async () => {
  try {
    const [sRes, uRes] = await Promise.all([
      apiClient.getStations(),
      apiClient.getUserDashboard(props.phone)
    ])
    if (!uRes || uRes.detail) {
      if (pollTimer) clearInterval(pollTimer)
      emit('logout')
      return
    }
    stations.value = sRes.stations || []
    if (selectedStation.value) {
      selectedStation.value = stations.value.find(s => s.stationName === selectedStation.value?.stationName) || null
    }
    if (uRes.user) user.value = uRes.user
    history.value = uRes.history || []
    withdrawals.value = uRes.withdrawals || []
  } catch {
    if (pollTimer) clearInterval(pollTimer)
  }
}

const handleDrop = async (deviceNo: string, positionNo: number, weight: number, label: string) => {
  loading.value = true
  errorToast.value = ''
  try {
    await apiClient.triggerDrop(deviceNo, positionNo, props.phone, weight)
    toast.value = `Submitted ${weight}kg of ${label}! Points placed in PENDING escrow awaiting Admin verification.`
    showQrModal.value = false
    await loadData()
    setTimeout(() => { toast.value = '' }, 5000)
  } catch (e: any) {
    errorToast.value = e.message
  } finally {
    loading.value = false
  }
}

const handleWithdrawSubmit = async () => {
  errorToast.value = ''
  try {
    await apiClient.createWithdrawal({
      phone: props.phone,
      amount_points: Number(withdrawPoints.value),
      bank_name: bankName.value,
      account_no: accountNo.value,
      account_holder_name: accountHolder.value
    })
    toast.value = 'Withdrawal request submitted! Waiting for Merchant Admin bank transfer.'
    accountNo.value = ''
    await loadData()
    setTimeout(() => { toast.value = '' }, 5000)
  } catch (e: any) {
    errorToast.value = e.message
  }
}

const handleDeleteAccount = async () => {
  if (!confirm('PDPA Data Deletion: Are you sure you want to permanently wipe your account and all test logs?')) return
  if (pollTimer) clearInterval(pollTimer)
  await apiClient.deleteAccount(props.phone)
  emit('logout')
}

let pollTimer: any = null

onMounted(() => {
  loadData()
  pollTimer = setInterval(loadData, 8000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

</script>

<template>
  <div class="min-h-screen bg-slate-100 text-slate-800 pb-24">
    <div class="max-w-md mx-auto min-h-screen bg-slate-50 shadow-xl relative pb-20">
      <!-- Toast Alerts -->
      <div v-if="toast" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-80 p-3 rounded-xl bg-emerald-600 text-white text-xs font-semibold shadow-lg">
        ✅ {{ toast }}
      </div>
      <div v-if="errorToast" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-80 p-3 rounded-xl bg-rose-600 text-white text-xs font-semibold shadow-lg">
        ⚠️ {{ errorToast }}
      </div>

      <!-- STATION DETAILS & MAPS NAVIGATION SCREEN -->
      <StationDetailView
        v-if="selectedStation"
        :station="selectedStation"
        :loading="loading"
        @back="selectedStation = null"
        @drop="p => handleDrop(p.deviceNo, p.positionNo, p.weight, p.label)"
      />


      <!-- SCREEN 6: HOMEPAGE -->
      <div v-else-if="activeScreen === 'home'"class="p-4 space-y-5">
        <!-- Top User Header -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-lg shadow">
              {{ user.nickname.charAt(0) }}
            </div>
            <div>
              <p class="font-bold text-sm text-slate-900">Hello, {{ user.nickname }}</p>
              <p class="text-xs text-slate-500">Ready to recycle today?</p>
            </div>
          </div>
          <span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">EN</span>
        </div>

        <!-- Promo Banner -->
        <div class="rounded-2xl bg-gradient-to-r from-emerald-700 to-teal-600 text-white p-5 shadow-md">
          <p class="text-xs uppercase tracking-wider font-semibold text-emerald-200">Rakyat Eco Initiative</p>
          <h2 class="text-xl font-extrabold mt-1">SAVE THE EARTH 🌍</h2>
          <p class="text-xs text-emerald-100 mt-1">Recycle Plastic, Cans, Paper & Used Cooking Oil (UCO) at 2-in-1 Stations.</p>
        </div>

        <!-- Dual Impact Card (Clickable to /history and /withdraw!) -->
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 grid grid-cols-2 divide-x divide-slate-200">
          <button @click="activeScreen = 'history'" class="pr-3 text-left hover:bg-slate-50 rounded-l-xl transition">
            <div class="flex items-center gap-2 text-emerald-600 text-xs font-bold">
              <span>⚖️</span><span>DELIVERED WEIGHT</span>
            </div>
            <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ user.total_recycled_kg }}<span class="text-sm font-normal"> kg</span></p>
            <p class="text-[11px] text-emerald-600 font-medium mt-1">View History →</p>
          </button>

          <button @click="activeScreen = 'withdraw'" class="pl-4 text-left hover:bg-slate-50 rounded-r-xl transition">
            <div class="flex items-center gap-2 text-amber-600 text-xs font-bold">
              <span>🪙</span><span>BALANCE</span>
            </div>
            <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ user.points_balance }}<span class="text-sm font-normal"> pts</span></p>
            <span v-if="user.pending_points > 0" class="inline-block mt-1 px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-[11px] font-bold">
              +{{ user.pending_points }} pending
            </span>
            <p v-else class="text-[11px] text-blue-600 font-medium mt-1">Withdraw RM →</p>
          </button>
        </div>

        <!-- Nearby Stations Section -->
        <div>
          <div class="flex justify-between items-center mb-3">
            <h3 class="font-bold text-sm text-slate-800">📍 Nearby Stations</h3>
            <span class="text-xs text-emerald-600 font-semibold">{{ stations.length }} Active Hubs</span>
          </div>

          <div class="space-y-4">
            <div
              v-for="st in stations"
              :key="st.stationName"
              @click="selectedStation = st"
              class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 space-y-3 cursor-pointer hover:border-emerald-500 transition"
            >

              <div class="flex justify-between items-start">
                <div>
                  <span :class="st.isOnline ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                    ● {{ st.isOnline ? 'Online' : 'Maintenance' }}
                  </span>
                  <h4 class="font-bold text-base text-slate-900 mt-1">{{ st.stationName }}</h4>
                  <p class="text-xs text-slate-500">{{ st.address }}</p>
                </div>
                <div class="text-right">
                  <span class="text-xs font-bold text-slate-600">{{ st.distanceKm }} km</span>
                  <div class="mt-1 px-2.5 py-1 bg-emerald-600 text-white text-xs font-bold rounded-lg">GO ↗</div>
                </div>
              </div>

              <!-- Live Compartment Fullness Bars -->
              <div class="space-y-2 pt-2 border-t border-slate-100">
                <div v-for="bin in st.bins" :key="bin.deviceNo + '-' + bin.positionNo" class="text-xs">
                  <div class="flex justify-between mb-1">
                    <span class="font-semibold text-slate-700">{{ bin.rubbishTypeName }}</span>
                    <span :class="bin.fillPercent >= 80 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold'">
                      {{ bin.statusLabel }} ({{ bin.fillPercent }}%)
                    </span>
                  </div>
                  <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div :class="bin.fillPercent >= 95 ? 'bg-rose-500' : (bin.fillPercent >= 80 ? 'bg-amber-500' : 'bg-emerald-500')"
                      class="h-full transition-all" :style="{ width: bin.fillPercent + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SCREEN 7: WITHDRAW PAGE -->
      <div v-else-if="activeScreen === 'withdraw'" class="p-4 space-y-5">
        <div class="flex items-center gap-3">
          <button @click="activeScreen = 'home'" class="px-3 py-1.5 bg-white border rounded-xl text-sm font-bold">← Back</button>
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
          <button @click="handleWithdrawSubmit" class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow transition">
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

      <!-- SCREEN 8: RECYCLING HISTORY -->
      <div v-else-if="activeScreen === 'history'" class="p-4 space-y-4">
        <div class="rounded-2xl bg-emerald-600 text-white p-5 shadow">
          <button @click="activeScreen = 'home'" class="text-xs font-bold bg-emerald-700 px-2.5 py-1 rounded-lg mb-2">← Back</button>
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

      <!-- SCREEN 9: PROFILE PAGE -->
      <div v-else-if="activeScreen === 'profile'" class="p-4 space-y-5">
        <div class="rounded-2xl bg-emerald-600 text-white p-6 text-center shadow">
          <div class="w-16 h-16 mx-auto rounded-full bg-white text-emerald-700 font-extrabold text-2xl flex items-center justify-center shadow">
            {{ user.nickname.charAt(0) }}
          </div>
          <h2 class="text-lg font-bold mt-2">{{ user.nickname }}</h2>
          <p class="text-xs text-emerald-100">Phone: +60 {{ user.phone }} | Card: {{ user.card_code }}</p>
        </div>

        <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 space-y-3">
          <button @click="emit('logout')" class="w-full py-3 bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold rounded-xl text-sm transition">
            Switch Account / Logout
          </button>
          <button @click="handleDeleteAccount" class="w-full py-3 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 font-bold rounded-xl text-sm transition">
            🗑️ Delete My Account & Data (PDPA)
          </button>
        </div>
      </div>

      <!-- FLOATING QR SCAN / HARDWARE DROP MODAL -->
      <div v-if="showQrModal" class="fixed inset-0 bg-black/60 z-50 flex items-end sm:items-center justify-center p-4">
        <div class="bg-white w-full max-w-sm rounded-3xl p-5 space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="font-bold text-base">📷 Simulate Kiosk QR Scan & Drop</h3>
            <button @click="showQrModal = false" class="text-slate-400 font-bold">✕</button>
          </div>
          <p class="text-xs text-slate-500">Select a compartment at <b>Eco Botanic Mall</b> to simulate a recycling submission (starts in <b>PENDING</b> escrow until Admin approves):</p>
          <div class="space-y-2">
            <button :disabled="loading" @click="handleDrop('RVM-SK-001', 1, 1.25, 'Plastic & Can')" class="w-full p-3 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 rounded-xl text-left flex justify-between items-center">
              <div>
                <p class="font-bold text-sm text-emerald-900">♻️ Dry RVM: Plastic & Can</p>
                <p class="text-[11px] text-emerald-700">Includes Before/After Camera Snapshot URLs</p>
              </div>
              <span class="font-bold text-xs bg-emerald-600 text-white px-2.5 py-1 rounded-lg">+1.25 kg</span>
            </button>
            <button :disabled="loading" @click="handleDrop('UCO-SK-001', 1, 2.0, 'Used Cooking Oil')" class="w-full p-3 bg-amber-50 hover:bg-amber-100 border border-amber-300 rounded-xl text-left flex justify-between items-center">
              <div>
                <p class="font-bold text-sm text-amber-900">🛢️ UCO Unit: Used Cooking Oil</p>
                <p class="text-[11px] text-amber-700">Sensor-verified fluid weight (No camera photo)</p>
              </div>
              <span class="font-bold text-xs bg-amber-600 text-white px-2.5 py-1 rounded-lg">+2.00 kg</span>
            </button>
          </div>
        </div>
      </div>

      <!-- BOTTOM MOBILE NAVBAR (Matching UI Flow.png!) -->
      <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-slate-200 px-8 py-2.5 flex justify-between items-center z-40">
        <button @click="activeScreen = 'home'" :class="activeScreen === 'home' ? 'text-emerald-600 font-bold' : 'text-slate-400'" class="flex flex-col items-center text-xs">
          <span class="text-lg">🏠</span><span>Home</span>
        </button>
        <button @click="showQrModal = true" class="-mt-8 w-14 h-14 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg flex items-center justify-center text-2xl border-4 border-white">
          📷
        </button>
        <button @click="activeScreen = 'profile'" :class="activeScreen === 'profile' ? 'text-emerald-600 font-bold' : 'text-slate-400'" class="flex flex-col items-center text-xs">
          <span class="text-lg">👤</span><span>Profile</span>
        </button>
      </nav>
    </div>
  </div>
</template>
