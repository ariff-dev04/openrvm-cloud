<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { apiClient } from '../../core/api'
import type { UserAccount, StationGroup, SubmissionItem, WithdrawalItem } from '../../core/types'

import StationDetailView from './StationDetailView.vue'
import HomeView from './views/HomeView.vue'
import WithdrawView from './views/WithdrawView.vue'
import HistoryView from './views/HistoryView.vue'
import ProfileView from './views/ProfileView.vue'

const props = defineProps<{ phone: string }>()
const emit = defineEmits<{ (e: 'logout'): void }>()

const activeScreen = ref<'home' | 'withdraw' | 'history' | 'profile'>('home')
const selectedStation = ref<StationGroup | null>(null)
const showQrModal = ref(false)
const toast = ref('')
const errorToast = ref('')
const loading = ref(false)

const user = ref<UserAccount>({
  id: 1,
  phone: props.phone,
  nickname: 'Ariff Bin Zakaria',
  points_balance: 1500,
  pending_points: 62.5,
  total_recycled_kg: 12.5,
  is_verified: true
})
const stations = ref<StationGroup[]>([])
const history = ref<SubmissionItem[]>([])
const withdrawals = ref<WithdrawalItem[]>([])

let pollTimer: any = null

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
      selectedStation.value =
        stations.value.find(s => s.stationName === selectedStation.value?.stationName) || null
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

const handleWithdrawSubmit = async (payload: { amount_points: number; bank_name: string; account_no: string; account_holder_name: string }) => {
  errorToast.value = ''
  try {
    await apiClient.createWithdrawal({ phone: props.phone, ...payload })
    toast.value = 'Withdrawal request submitted! Waiting for Merchant Admin bank transfer.'
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
      <div v-if="toast" class="fixed top-10 left-1/2 -translate-x-1/2 z-50 w-80 p-3 rounded-xl bg-emerald-600 text-white text-xs font-semibold shadow-lg">
        ✅ {{ toast }}
      </div>
      <div v-if="errorToast" class="fixed top-10 left-1/2 -translate-x-1/2 z-50 w-80 p-3 rounded-xl bg-rose-600 text-white text-xs font-semibold shadow-lg">
        ⚠️ {{ errorToast }}
      </div>

      <!-- MODULAR RECYCLER VIEWS -->
      <StationDetailView
        v-if="selectedStation"
        :station="selectedStation"
        :loading="loading"
        @back="selectedStation = null"
        @drop="p => handleDrop(p.deviceNo, p.positionNo, p.weight, p.label)"
      />
      <HomeView
        v-else-if="activeScreen === 'home'"
        :user="user"
        :stations="stations"
        @navigate="scr => activeScreen = scr"
        @select-station="st => selectedStation = st"
      />
      <WithdrawView
        v-else-if="activeScreen === 'withdraw'"
        :user="user"
        :withdrawals="withdrawals"
        @back="activeScreen = 'home'"
        @submit="handleWithdrawSubmit"
      />
      <HistoryView
        v-else-if="activeScreen === 'history'"
        :user="user"
        :history="history"
        @back="activeScreen = 'home'"
      />
      <ProfileView
        v-else-if="activeScreen === 'profile'"
        :user="user"
        @logout="emit('logout')"
        @delete-account="handleDeleteAccount"
      />

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

      <!-- BOTTOM MOBILE NAVBAR -->
      <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-slate-200 px-8 py-2.5 flex justify-between items-center z-40">
        <button @click="selectedStation = null; activeScreen = 'home'" :class="activeScreen === 'home' && !selectedStation ? 'text-emerald-600 font-bold' : 'text-slate-400'" class="flex flex-col items-center text-xs">
          <span class="text-lg">🏠</span><span>Home</span>
        </button>
        <button @click="showQrModal = true" class="-mt-8 w-14 h-14 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg flex items-center justify-center text-2xl border-4 border-white">
          📷
        </button>
        <button @click="selectedStation = null; activeScreen = 'profile'" :class="activeScreen === 'profile' && !selectedStation ? 'text-emerald-600 font-bold' : 'text-slate-400'" class="flex flex-col items-center text-xs">
          <span class="text-lg">👤</span><span>Profile</span>
        </button>
      </nav>
    </div>
  </div>
</template>
