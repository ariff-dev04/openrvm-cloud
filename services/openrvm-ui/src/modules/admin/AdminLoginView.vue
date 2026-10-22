<script setup lang="ts">
import { ref } from 'vue'
import { apiClient } from '../../core/api'

const emit = defineEmits<{ (e: 'logged-in', admin: any): void }>()

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await apiClient.adminLogin(email.value, password.value)
    emit('logged-in', res.admin)
  } catch (e: any) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

const loginAsGuestRecruiter = async () => {
  email.value = 'demo@openrvm.my'
  password.value = 'demo123'
  await handleLogin()
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center p-4 text-slate-100">
    <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
      <div class="flex items-center gap-3">
        <div class="w-11 h-11 rounded-2xl bg-emerald-600 text-white font-extrabold flex items-center justify-center text-xl">R</div>
        <div>
          <h1 class="text-lg font-extrabold">OpenRVM Merchant Admin</h1>
          <p class="text-xs text-slate-400">Role-Based Access Control (RBAC) Portal</p>
        </div>
      </div>

      <!-- PUBLIC RECRUITER SANDBOX BANNER -->
      <div class="p-4 rounded-2xl bg-indigo-950/60 border border-indigo-500/40 space-y-2.5">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-indigo-300 uppercase tracking-wider">👋 Visiting Recruiter / Tester?</span>
          <span class="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 rounded text-[10px] font-bold">READ-ONLY SANDBOX</span>
        </div>
        <p class="text-xs text-slate-300">Explore all dashboards, Before/After camera snapshots, and payout modals safely without altering live database records.</p>
        <button @click="loginAsGuestRecruiter" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs shadow transition">
          👁️ Enter Recruiter Read-Only Demo (demo@openrvm.my)
        </button>
      </div>

      <div class="relative flex py-1 items-center">
        <div class="flex-grow border-t border-slate-800"></div>
        <span class="flex-shrink mx-3 text-[11px] text-slate-500 font-bold uppercase">Or Developer Master Sign In</span>
        <div class="flex-grow border-t border-slate-800"></div>
      </div>

      <!-- DEVELOPER / STAFF LOGIN FORM -->
      <div class="space-y-4">
        <div>
          <label class="text-xs font-bold text-slate-400 uppercase">Staff / Master Email</label>
          <input v-model="email" type="email" placeholder="Enter authorized staff email..." class="w-full mt-1 px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-sm outline-none focus:border-emerald-500" />
        </div>
        <div>
          <label class="text-xs font-bold text-slate-400 uppercase">Password</label>
          <input v-model="password" type="password" placeholder="••••••••••••" @keyup.enter="handleLogin" class="w-full mt-1 px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-sm outline-none focus:border-emerald-500" />
        </div>
        <p v-if="errorMsg" class="text-xs text-rose-400 font-bold">⚠️ {{ errorMsg }}</p>
        <button :disabled="loading" @click="handleLogin" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg transition">
          {{ loading ? 'Authenticating...' : 'Sign In with Staff Credentials →' }}
        </button>
      </div>
    </div>
  </div>
</template>
