<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../core/api'

const emit = defineEmits<{ (e: 'authenticated', phone: string): void }>()

interface SavedGoogleAccount {
  email: string
  nickname: string
  phone: string
}

const step = ref<'welcome' | 'login' | 'phone' | 'otp' | 'success'>('welcome')
const lang = ref<'EN' | 'BM' | 'ZH'>('EN')
const showGooglePopup = ref(false)
const isNewGoogleAccount = ref(false)
const googleName = ref('')
const googleEmail = ref('')
const phoneInput = ref('')
const otpDigits = ref<string[]>(['', '', '', ''])
const generatedOtpHint = ref('')
const errorMsg = ref('')
const savedAccounts = ref<SavedGoogleAccount[]>([])

onMounted(() => {
  try {
    const raw = localStorage.getItem('openrvm_known_accounts')
    if (raw) savedAccounts.value = JSON.parse(raw)
  } catch {
    savedAccounts.value = []
  }
})

const saveKnownAccount = (email: string, nickname: string, phone: string) => {
  const list = savedAccounts.value.filter(a => a.email.toLowerCase() !== email.toLowerCase() && a.phone !== phone)
  list.unshift({ email, nickname, phone })
  savedAccounts.value = list.slice(0, 5)
  localStorage.setItem('openrvm_known_accounts', JSON.stringify(savedAccounts.value))
}

const quickSelectSavedAccount = async (acc: SavedGoogleAccount) => {
  errorMsg.value = ''
  const res = await apiClient.checkGoogleAccount(acc.email, acc.nickname)
  if (res.status === 'EXISTING_VERIFIED' && res.user?.phone) {
    emit('authenticated', res.user.phone)
  } else {
    // Account was deleted from DB earlier -> re-verify phone
    googleEmail.value = acc.email
    googleName.value = acc.nickname
    phoneInput.value = acc.phone
    showGooglePopup.value = false
    step.value = 'phone'
  }
}

const confirmGoogleAccount = async () => {
  if (!googleEmail.value) {
    errorMsg.value = 'Please enter your Google Email'
    return
  }
  errorMsg.value = ''
  // Check PostgreSQL first: if this Google email already bound & verified OTP previously, sign straight in!
  const res = await apiClient.checkGoogleAccount(googleEmail.value, googleName.value || 'Recycler')
  if (res.status === 'EXISTING_VERIFIED' && res.user?.phone) {
    saveKnownAccount(res.user.google_email || googleEmail.value, res.user.nickname, res.user.phone)
    showGooglePopup.value = false
    emit('authenticated', res.user.phone)
    return
  }

  // Otherwise, new email -> require Name & proceed to 1-time Phone OTP binding
  if (!googleName.value) {
    isNewGoogleAccount.value = true
    errorMsg.value = 'First-time sign in detected! Please enter your Name to bind your RVM phone number.'
    return
  }
  showGooglePopup.value = false
  step.value = 'phone'
}

const handleSendOtp = async () => {
  const cleanPhone = phoneInput.value.replace(/\D/g, '')
  if (cleanPhone.length < 8) {
    errorMsg.value = 'Please enter a valid Malaysian phone number'
    return
  }
  phoneInput.value = cleanPhone
  errorMsg.value = ''
  try {
    const res = await apiClient.sendOtp(cleanPhone, googleName.value || 'Recycler', googleEmail.value || 'user@gmail.com')
    generatedOtpHint.value = res.demo_otp
    otpDigits.value = ['', '', '', '']
    step.value = 'otp'
  } catch (e: any) {
    errorMsg.value = e.message || 'Phone number already bound to another account'
  }
}


const handleVerifyOtp = async () => {
  errorMsg.value = ''
  try {
    await apiClient.verifyOtp(phoneInput.value, otpDigits.value.join(''))
    saveKnownAccount(googleEmail.value || 'user@gmail.com', googleName.value || 'Recycler', phoneInput.value)
    step.value = 'success'
  } catch (e: any) {
    errorMsg.value = e.message || 'Invalid 4-digit OTP'
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-100 flex items-center justify-center p-4 text-slate-800">
    <div class="w-full max-w-sm bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden p-6 relative">
      <!-- Language Selector -->
      <div class="flex justify-end mb-4">
        <div class="inline-flex bg-slate-100 rounded-full p-1 text-xs font-semibold">
          <button v-for="l in (['EN', 'BM', 'ZH'] as const)" :key="l" @click="lang = l"
            :class="lang === l ? 'bg-emerald-600 text-white shadow' : 'text-slate-500'"
            class="px-2.5 py-1 rounded-full transition">
            {{ l }}
          </button>
        </div>
      </div>

      <!-- STEP 1: WELCOME PAGE -->
      <div v-if="step === 'welcome'" class="text-center py-6 space-y-5">
        <div class="w-24 h-24 mx-auto rounded-full bg-emerald-50 border-2 border-emerald-500 flex items-center justify-center text-4xl shadow-inner">
          ♻️
        </div>
        <div>
          <h1 class="text-2xl font-extrabold text-slate-900">Smart Recycle Web</h1>
          <p class="text-sm text-slate-500 mt-1">Recycle Smart, Earn Rewards</p>
        </div>
        <button @click="step = 'login'" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-full shadow-lg transition">
          Get Started
        </button>
      </div>

      <!-- STEP 2: SIGN IN WITH GOOGLE -->
      <div v-else-if="step === 'login'" class="text-center py-6 space-y-5">
        <div class="w-20 h-20 mx-auto rounded-2xl bg-emerald-50 flex items-center justify-center text-3xl">🌱</div>
        <div>
          <h2 class="text-xl font-bold text-slate-900">Welcome Back</h2>
          <p class="text-xs text-slate-500 mt-1">Returning users sign in directly; new users bind their phone once via OTP</p>
        </div>
        <button @click="showGooglePopup = true; isNewGoogleAccount = false; errorMsg = ''" class="w-full py-3.5 px-4 border border-slate-300 hover:bg-slate-50 rounded-xl font-semibold text-sm flex items-center justify-center gap-3 shadow-sm transition">
          <span class="text-lg font-extrabold text-blue-600">G</span>
          <span>Sign in with Google</span>
        </button>
        <div class="pt-3 border-t border-slate-100">
          <button @click="emit('authenticated', '0123456789')" class="w-full py-2 text-xs text-slate-500 hover:text-emerald-700 font-semibold">
            👁️ Preview Pre-Seeded Demo Account (ariff.ukm@gmail.com)
          </button>
        </div>
      </div>

      <!-- GOOGLE OAUTH ACCOUNT PICKER MODAL -->
      <div v-if="showGooglePopup" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-xs rounded-2xl p-5 shadow-2xl space-y-4 text-left">
          <div class="flex items-center gap-2 border-b pb-3">
            <span class="text-xl font-extrabold text-blue-600">G</span>
            <div>
              <p class="font-bold text-sm text-slate-900">Choose an account</p>
              <p class="text-[11px] text-slate-400">to continue to OpenRVM Cloud</p>
            </div>
          </div>

          <!-- 1-Tap Returning Verified Accounts -->
          <div v-if="savedAccounts.length > 0 && !isNewGoogleAccount" class="space-y-1.5">
            <p class="text-[11px] font-bold text-slate-400 uppercase">Verified on this device</p>
            <button v-for="acc in savedAccounts" :key="acc.email" @click="quickSelectSavedAccount(acc)"
              class="w-full p-2.5 rounded-xl border border-slate-200 hover:bg-emerald-50 hover:border-emerald-300 flex items-center gap-3 text-left transition">
              <div class="w-8 h-8 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-xs shrink-0">
                {{ acc.nickname.charAt(0) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="font-bold text-xs text-slate-900 truncate">{{ acc.nickname }}</p>
                <p class="text-[11px] text-slate-500 truncate">{{ acc.email }} • +60{{ acc.phone }}</p>
              </div>
            </button>
          </div>

          <div class="space-y-3 pt-1">
            <div>
              <label class="text-xs font-bold text-slate-600">Google Email</label>
              <input v-model="googleEmail" type="email" placeholder="yourname@gmail.com" @keyup.enter="confirmGoogleAccount" class="w-full mt-1 px-3 py-2 border rounded-xl text-xs" />
              <p class="text-[10px] text-slate-400 mt-1">Already verified? Just enter your email to sign right in!</p>
            </div>
            <div v-if="isNewGoogleAccount">
              <label class="text-xs font-bold text-slate-600">Your Full Name (First-time setup)</label>
              <input v-model="googleName" type="text" placeholder="e.g. Ahmad Razak" class="w-full mt-1 px-3 py-2 border border-emerald-500 rounded-xl text-xs" />
            </div>
            <p v-if="errorMsg" class="text-xs text-rose-600 font-bold">{{ errorMsg }}</p>
            <div class="flex gap-2 pt-1">
              <button @click="showGooglePopup = false" class="flex-1 py-2 bg-slate-100 rounded-xl text-xs font-bold">Cancel</button>
              <button @click="confirmGoogleAccount" class="flex-1 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold">Continue →</button>
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 3: PHONE NUMBER BINDING -->
      <div v-else-if="step === 'phone'" class="py-4 space-y-5">
        <div class="w-16 h-16 mx-auto rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center text-2xl">🛡️</div>
        <div class="text-center">
          <h2 class="text-lg font-bold">1-Time Phone Binding</h2>
          <p class="text-xs text-slate-500 mt-1">Hi <b>{{ googleName }}</b>! Link your phone number once so RVM kiosks recognize you:</p>
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-600">Malaysian Phone Number</label>
          <div class="flex items-center mt-1 border border-slate-300 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-emerald-500">
            <span class="bg-slate-100 px-3 py-3 text-sm font-bold text-slate-600 border-r border-slate-300">🇲🇾 +60</span>
            <input v-model="phoneInput" type="text" placeholder="0198765432" class="w-full px-3 py-3 text-sm outline-none font-mono" />
          </div>
        </div>
        <p v-if="errorMsg" class="text-xs text-rose-600 font-bold">{{ errorMsg }}</p>
        <button @click="handleSendOtp" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-full shadow transition">
          Send 4-Digit OTP
        </button>
      </div>

      <!-- STEP 4: 4-DIGIT OTP CODE -->
      <div v-else-if="step === 'otp'" class="py-4 space-y-5 text-center">
        <h2 class="text-lg font-bold">Verification Code</h2>
        <p class="text-xs text-slate-500">Enter the 4-digit OTP generated for <span class="font-bold text-slate-700">+60 {{ phoneInput }}</span></p>
        <div class="p-2.5 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-900">
          🔐 Encrypted Redis OTP (5m TTL): <span class="font-mono font-extrabold text-sm">{{ generatedOtpHint }}</span>
          <button @click="otpDigits = generatedOtpHint.split('')" class="ml-2 underline text-emerald-700 font-bold">Auto-fill</button>
        </div>
        <div class="flex justify-center gap-3 my-4">
          <input v-for="(_, idx) in 4" :key="idx" v-model="otpDigits[idx]" maxlength="1"
            class="w-12 h-14 text-center text-xl font-bold border-2 border-emerald-500 rounded-xl bg-slate-50 outline-none" />
        </div>
        <p v-if="errorMsg" class="text-xs text-rose-600 font-semibold">{{ errorMsg }}</p>
        <button @click="handleVerifyOtp" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-full shadow transition">
          Confirm
        </button>
      </div>

      <!-- STEP 5: SUCCESS SCREEN -->
      <div v-else-if="step === 'success'" class="py-8 text-center space-y-5">
        <div class="w-20 h-20 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-4xl">✓</div>
        <div>
          <h2 class="text-xl font-extrabold text-slate-900">Success!</h2>
          <p class="text-xs text-slate-500 mt-1">Your email (<b>{{ googleEmail }}</b>) is now permanently bound to <b>+60 {{ phoneInput }}</b>. Next time you sign in, you will go straight to the Homepage!</p>
        </div>
        <button @click="emit('authenticated', phoneInput)" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-full shadow transition">
          Continue to Homepage
        </button>
      </div>
    </div>
  </div>
</template>
