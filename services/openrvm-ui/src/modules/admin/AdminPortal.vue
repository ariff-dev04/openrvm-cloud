<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../core/api'
import type { SubmissionItem, WithdrawalItem, UserAccount } from '../../core/types'

import AdminLoginView from './AdminLoginView.vue'
import DashboardTab from './tabs/DashboardTab.vue'
import SubmissionsTab from './tabs/SubmissionsTab.vue'
import MachinesTab from './tabs/MachinesTab.vue'
import WithdrawalsTab from './tabs/WithdrawalsTab.vue'
import UsersTab from './tabs/UsersTab.vue'
import WasteLogsTab from './tabs/WasteLogsTab.vue'
import AdminAccessTab from './tabs/AdminAccessTab.vue'

type TabKey = 'dashboard' | 'submissions' | 'withdrawals' | 'machines' | 'users' | 'logs' | 'access'

const currentAdmin = ref<any>(null)
const activeTab = ref<TabKey>('dashboard')
const topTabs: TabKey[] = ['dashboard', 'submissions', 'withdrawals', 'machines']

const kpis = ref({ pendingWithdrawals: 0, onlineMachines: '0 / 0', totalPoints: 0, recycledWeightKg: 0, lastSynced: 'Just now', syncRuns: 0 })
const submissions = ref<SubmissionItem[]>([])
const withdrawals = ref<WithdrawalItem[]>([])
const machines = ref<any[]>([])
const cleaningLogs = ref<any[]>([])
const users = ref<UserAccount[]>([])
const toast = ref('')

const loadOverview = async () => {
  const data = await apiClient.getAdminOverview()
  if (data.kpis) kpis.value = data.kpis
  submissions.value = data.submissions || []
  withdrawals.value = data.withdrawals || []
  machines.value = data.machines || []
  cleaningLogs.value = data.cleaningLogs || []
  users.value = data.users || []
}

const showToast = (msg: string) => {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 4000)
}

onMounted(() => {
  loadOverview()
  setInterval(loadOverview, 8000)
})
</script>

<template>
  <!-- GATEKEEPER: Admin RBAC Login -->
  <AdminLoginView v-if="!currentAdmin" @logged-in="adm => currentAdmin = adm" />

  <!-- AUTHENTICATED WORKSPACE SHELL -->
  <div v-else class="min-h-screen bg-slate-100 text-slate-800 flex">
    <!-- LEFT SIDEBAR -->
    <aside class="w-56 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0">
      <div>
        <div class="p-4 border-b border-slate-200 flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-emerald-600 text-white font-extrabold flex items-center justify-center">R</div>
          <div>
            <p class="font-extrabold text-sm text-slate-900 leading-none">RVM Merchant</p>
            <p class="text-[11px] text-slate-400 mt-0.5">Admin Platform v2.0</p>
          </div>
        </div>
        <nav class="p-3 space-y-1 text-xs font-semibold">
          <button @click="activeTab = 'dashboard'" :class="activeTab === 'dashboard' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition"><span>📊</span><span>Dashboard</span></button>
          <button @click="activeTab = 'submissions'" :class="activeTab === 'submissions' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition"><span>✅</span><span>Submissions</span></button>
          <button @click="activeTab = 'withdrawals'" :class="activeTab === 'withdrawals' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition">
            <span>💸</span><span>Withdrawals</span>
            <span v-if="kpis.pendingWithdrawals > 0" class="ml-auto bg-amber-500 text-white px-1.5 py-0.5 rounded-full text-[10px]">{{ kpis.pendingWithdrawals }}</span>
          </button>
          <button @click="activeTab = 'users'" :class="activeTab === 'users' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition"><span>👥</span><span>Users</span></button>
          <button @click="activeTab = 'machines'" :class="activeTab === 'machines' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition"><span>🤖</span><span>Machines</span></button>
          <button @click="activeTab = 'logs'" :class="activeTab === 'logs' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition"><span>🚛</span><span>Waste Logs</span></button>
          <button @click="activeTab = 'access'" :class="activeTab === 'access' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition"><span>🛡️</span><span>Admin Access</span></button>
        </nav>
      </div>
      <div class="p-3 border-t border-slate-200 space-y-2 text-xs">
        <div class="text-slate-400">
          <p class="font-semibold text-slate-600">System Health</p>
          <p class="text-emerald-600 font-bold mt-0.5">● Operational ({{ kpis.syncRuns }} syncs)</p>
        </div>
        <button @click="currentAdmin = null" class="w-full py-2 bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-600 font-bold rounded-xl transition">
          🚪 Logout
        </button>
      </div>
    </aside>

    <!-- MAIN CONTENT AREA -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="bg-white border-b border-slate-200 px-6 py-2.5 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <button v-for="t in topTabs" :key="t" @click="activeTab = t"
            :class="activeTab === t ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            class="px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition">
            {{ t === 'machines' ? 'Machine Status' : t }}
          </button>
        </div>
        <div class="flex items-center gap-3 text-xs">
          <span class="text-slate-400">Last synced: {{ kpis.lastSynced }}</span>
          <span class="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold">
            👤 {{ currentAdmin.full_name }} ({{ currentAdmin.role }})
          </span>
        </div>
      </header>

      <div v-if="toast" class="mx-6 mt-4 p-3 rounded-xl bg-emerald-600 text-white text-xs font-bold shadow">
        ✅ {{ toast }}
      </div>

      <!-- MODULAR TAB VIEWS -->
      <DashboardTab v-if="activeTab === 'dashboard'" :kpis="kpis" :submissions="submissions" :cleaningLogs="cleaningLogs" :withdrawals="withdrawals" @navigate="t => activeTab = t" />
      <SubmissionsTab v-else-if="activeTab === 'submissions'" :submissions="submissions" @refresh="loadOverview" @notify="showToast" />
      <MachinesTab v-else-if="activeTab === 'machines'" :machines="machines" @refresh="loadOverview" @notify="showToast" />
      <WithdrawalsTab v-else-if="activeTab === 'withdrawals'" :withdrawals="withdrawals" @refresh="loadOverview" @notify="showToast" />
      <UsersTab v-else-if="activeTab === 'users'" :users="users" />
      <WasteLogsTab v-else-if="activeTab === 'logs'" :logs="cleaningLogs" />
      <AdminAccessTab v-else-if="activeTab === 'access'" :currentAdmin="currentAdmin" />
    </div>
  </div>
</template>
