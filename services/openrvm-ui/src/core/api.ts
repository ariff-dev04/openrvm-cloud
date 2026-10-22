const getAdminRoleHeader = (): Record<string, string> => {
  try {
    const raw = localStorage.getItem('openrvm_admin_session')
    if (!raw) return {}
    const adm = JSON.parse(raw)
    return { 'X-Admin-Role': adm.role || 'GUEST_AUDITOR' }
  } catch {
    return {}
  }
}

export const apiClient = {
  async checkGoogleAccount(email: string, nickname: string) {
    const r = await fetch('/api/auth/google-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, nickname })
    })
    return r.json()
  },

  async getStations() {
    const r = await fetch('/api/stations')
    return r.json()
  },
  async getUserDashboard(phone: string) {
    const r = await fetch(`/api/user/${phone}/dashboard`)
    return r.json()
  },
  async sendOtp(phone: string, nickname: string, email: string) {
    const r = await fetch('/api/auth/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, nickname, email })
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Failed to send OTP')
    return data
  },
  async verifyOtp(phone: string, code: string) {
    const r = await fetch('/api/auth/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, code })
    })
    if (!r.ok) throw new Error('Invalid 4-digit OTP code')
    return r.json()
  },
  async deleteAccount(phone: string) {
    const r = await fetch(`/api/auth/account/${phone}`, { method: 'DELETE' })
    return r.json()
  },
  async triggerDrop(deviceNo: string, positionNo: number, phone: string, addedWeightKg: number) {
    const r = await fetch('/api/simulator/drop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deviceNo, positionNo, phone, addedWeightKg })
    })
    if (!r.ok) {
      const err = await r.json()
      throw new Error(err.detail || 'Drop failed')
    }
    return r.json()
  },
  async createWithdrawal(payload: { phone: string; amount_points: number; bank_name: string; account_no: string; account_holder_name: string }) {
    const r = await fetch('/api/user/withdraw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Withdrawal request failed')
    return data
  },
  async getAdminOverview() {
    const r = await fetch('/api/admin/overview')
    return r.json()
  },
  async forceSync() {
    const r = await fetch('/api/admin/submissions/force-sync', { method: 'POST' })
    return r.json()
  },
  async auditSubmission(putId: number, action: 'VERIFIED' | 'CORRECTED' | 'REJECTED', actualWeightKg?: number) {
    const r = await fetch(`/api/admin/submissions/${putId}/audit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAdminRoleHeader() },
      body: JSON.stringify({ action, actual_weight_kg: actualWeightKg })
    })
    const data = await r.json()
    if (!r.ok) return { msg: `🔒 ${data.detail}` }
    return data
  },
  async auditWithdrawal(id: number, action: 'PAID' | 'REJECTED') {
    const r = await fetch(`/api/admin/withdrawals/${id}/audit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAdminRoleHeader() },
      body: JSON.stringify({ action })
    })
    const data = await r.json()
    if (!r.ok) return { msg: `🔒 ${data.detail}` }
    return data
  },
  async toggleMaintenance(deviceNo: string) {
    const r = await fetch(`/api/admin/machines/${deviceNo}/toggle-maintenance`, {
      method: 'POST',
      headers: { ...getAdminRoleHeader() }
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Read-only mode')
    return data
  },
  async adminLogin(email: string, password: string) {
    const r = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Admin login failed')
    localStorage.setItem('openrvm_admin_session', JSON.stringify(data.admin))
    return data
  },
  async getAdminAccounts() {
    const r = await fetch('/api/admin/accounts')
    return r.json()
  },
  async createAdminAccount(payload: { email: string; full_name: string; role: string; password: string }) {
    const r = await fetch('/api/admin/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAdminRoleHeader() },
      body: JSON.stringify(payload)
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Failed to create admin')
    return data
  },
  async deleteAdminAccount(id: number) {
    const r = await fetch(`/api/admin/accounts/${id}`, {
      method: 'DELETE',
      headers: { ...getAdminRoleHeader() }
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.detail || 'Failed to delete admin')
    return data
  }
}
