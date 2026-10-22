<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../../core/api'

const props = defineProps<{ currentAdmin: any }>()
const admins = ref<any[]>([])
const email = ref('')
const fullName = ref('')
const role = ref('OPERATOR')
const password = ref('')
const msg = ref('')

const loadAdmins = async () => {
  admins.value = await apiClient.getAdminAccounts()
}

const handleCreate = async () => {
  if (!email.value || !fullName.value || !password.value) return
  try {
    const res = await apiClient.createAdminAccount({ email: email.value, full_name: fullName.value, role: role.value, password: password.value })
    msg.value = res.msg
    email.value = ''; fullName.value = ''; password.value = ''
    await loadAdmins()
  } catch (e: any) {
    msg.value = e.message
  }
}

const handleDelete = async (id: number) => {
  await apiClient.deleteAdminAccount(id)
  await loadAdmins()
}

onMounted(loadAdmins)
</script>

<template>
  <main class="p-6 space-y-6">
    <div>
      <h1 class="text-xl font-extrabold text-slate-900">🛡️ Admin Access & RBAC Management</h1>
      <p class="text-xs text-slate-500">Master Admin portal to provision and revoke staff credentials</p>
    </div>

    <div v-if="msg" class="p-3 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold">{{ msg }}</div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Create New Admin Form -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <h3 class="font-bold text-sm text-slate-900">Provision New Staff Account</h3>
        <div>
          <label class="text-xs font-semibold text-slate-600">Full Name</label>
          <input v-model="fullName" type="text" placeholder="e.g. Siti Sarah (Auditor)" class="w-full mt-1 px-3 py-2 border rounded-xl text-xs" />
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-600">Staff Email</label>
          <input v-model="email" type="email" placeholder="siti@openrvm.my" class="w-full mt-1 px-3 py-2 border rounded-xl text-xs" />
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-600">Role</label>
          <select v-model="role" class="w-full mt-1 px-3 py-2 border rounded-xl text-xs bg-white">
            <option value="OPERATOR">OPERATOR (Submissions & Machines)</option>
            <option value="FINANCE">FINANCE (Withdrawals Payout)</option>
            <option value="SUPER_ADMIN">SUPER_ADMIN (Full Access)</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-600">Temporary Password</label>
          <input v-model="password" type="password" placeholder="••••••••" class="w-full mt-1 px-3 py-2 border rounded-xl text-xs" />
        </div>
        <button @click="handleCreate" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs shadow">
          + Create Admin Credential
        </button>
      </div>

      <!-- Existing Admins Table -->
      <div class="md:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase">
            <tr><th class="p-3.5">ID</th><th>Name</th><th>Email</th><th>Role</th><th>Created</th><th>Action</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            <tr v-for="a in admins" :key="a.id">
              <td class="p-3.5 font-mono">#{{ a.id }}</td>
              <td class="font-bold text-slate-900">{{ a.full_name }}</td>
              <td class="font-mono text-blue-700">{{ a.email }}</td>
              <td><span class="px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded font-bold text-[10px]">{{ a.role }}</span></td>
              <td class="text-slate-400">{{ a.created_at }}</td>
              <td>
                <button v-if="a.role !== 'SUPER_ADMIN'" @click="handleDelete(a.id)" class="px-2.5 py-1 bg-rose-50 text-rose-600 rounded font-bold">Revoke</button>
                <span v-else class="text-slate-400 italic">Primary</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</template>
