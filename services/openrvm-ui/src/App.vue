<script setup lang="ts">
import { ref } from 'vue'
import AuthFlow from './modules/auth/AuthFlow.vue'
import RecyclerPortal from './modules/recycler/RecyclerPortal.vue'
import AdminPortal from './modules/admin/AdminPortal.vue'

const hostname = window.location.hostname
const searchParams = new URLSearchParams(window.location.search)
const isHostAdmin = hostname.startsWith('admin.') || searchParams.get('portal') === 'admin'
const isStrictDomain = ref<boolean>(hostname.includes('ariff.lab'))

const activePortal = ref<'user' | 'admin'>(isHostAdmin ? 'admin' : 'user')
const showPortfolioBar = ref<boolean>(!isStrictDomain.value)

// Persist User Login Session in localStorage
const savedPhone = localStorage.getItem('openrvm_user_phone')
const isAuthenticated = ref<boolean>(!!savedPhone)
const currentPhone = ref<string>(savedPhone || '0123456789')

const onAuthenticated = (phone: string) => {
  currentPhone.value = phone
  isAuthenticated.value = true
  localStorage.setItem('openrvm_user_phone', phone)
}

const onLogout = () => {
  isAuthenticated.value = false
  localStorage.removeItem('openrvm_user_phone')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- SLIM TOP PORTFOLIO BAR (Never overlaps the mobile bottom navbar!) -->
    <div
      v-if="showPortfolioBar"
      class="bg-slate-950 text-slate-200 border-b border-slate-800 px-3 py-1.5 flex items-center justify-between text-[11px] font-bold z-50"
    >
      <span class="text-emerald-400 truncate hidden sm:inline">♻️ OpenRVM v2.0 Live Portfolio Demo</span>
      <div class="flex items-center gap-1.5 mx-auto sm:mx-0">
        <button
          @click="activePortal = 'user'"
          :class="activePortal === 'user' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'"
          class="px-2.5 py-1 rounded-md transition"
        >
          📱 User App
        </button>
        <button
          @click="activePortal = 'admin'"
          :class="activePortal === 'admin' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'"
          class="px-2.5 py-1 rounded-md transition"
        >
          🖥️ Admin Portal
        </button>
      </div>
      <button
        @click="showPortfolioBar = false"
        title="Hide Demo Bar"
        class="text-slate-500 hover:text-slate-300 px-1.5"
      >
        ✕
      </button>
    </div>

    <!-- 1. MERCHANT ADMIN PLATFORM -->
    <div class="flex-1">
      <AdminPortal v-if="activePortal === 'admin'" />

      <!-- 2. USER RECYCLER WEB APP -->
      <template v-else>
        <AuthFlow v-if="!isAuthenticated" @authenticated="onAuthenticated" />
        <RecyclerPortal v-else :phone="currentPhone" @logout="onLogout" />
      </template>
    </div>
  </div>
</template>
