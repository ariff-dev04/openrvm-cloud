export interface UserAccount {
  id: number
  phone: string
  google_email?: string
  nickname: string
  avatar_url?: string
  card_code?: string
  points_balance: number
  pending_points: number
  total_recycled_kg: number
  is_verified: boolean
}

export interface BinCompartment {
  deviceNo: string
  deviceType: 'DRY_2BIN' | 'UCO_OIL'
  positionNo: number
  rubbishTypeName: string
  ratePerKg: number
  currentWeight: number
  maxWeight: number
  fillPercent: number
  statusLabel: 'NORMAL' | 'ALMOST FULL' | 'FULL'
}

export interface StationGroup {
  stationName: string
  zone: string
  address: string
  latitude: number
  longitude: number
  distanceKm: number
  supportPhone?: string
  isOnline: boolean
  bins: BinCompartment[]
}

export interface SubmissionItem {
  put_id: number
  phone: string
  user_name: string
  device_no: string
  station_name: string
  device_type: 'DRY_2BIN' | 'UCO_OIL'
  rubbish_type: string
  rate_per_kg: number
  prev_bin_weight_kg: number
  bin_position_weight_kg: number
  submitted_weight_kg: number
  verified_weight_kg?: number | null
  snapshot_urls?: string | null
  points_awarded: number
  audit_status: 'PENDING' | 'VERIFIED' | 'REJECTED'
  created_at: string
}

export interface WithdrawalItem {
  id: number
  phone: string
  user_name: string
  amount_points: number
  amount_rm: number
  bank_name: string
  account_no: string
  account_holder_name: string
  status: 'PENDING' | 'PAID' | 'REJECTED'
  created_at: string
}
