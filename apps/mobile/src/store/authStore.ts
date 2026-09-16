import { create } from 'zustand'
import AsyncStorage from '@react-native-async-storage/async-storage'

const STORAGE_KEY = '@kpa_mobile_auth'

export interface User {
  id: string
  phone?: string | null
  name?: string | null
  role: string
  email?: string | null
  membership_no?: string | null
  studio_name?: string | null
  experience_years?: number | null
  district?: string | null
  taluka?: string | null
  is_active: boolean
  status?: string | null
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isHydrated: boolean
  setAuth: (user: User, token: string, refreshToken?: string | null) => void
  updateUser: (partialUser: Partial<User>) => void
  logout: () => void
  hydrate: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isHydrated: false,

  setAuth: (user, token, refreshToken = null) => {
    set({ user, token, refreshToken, isAuthenticated: true })
    AsyncStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ user, token, refreshToken })
    ).catch(() => {})
  },

  updateUser: (partialUser) => {
    const currentUser = get().user
    if (!currentUser) return
    const updated = { ...currentUser, ...partialUser }
    set({ user: updated })
    AsyncStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        user: updated,
        token: get().token,
        refreshToken: get().refreshToken,
      })
    ).catch(() => {})
  },

  logout: () => {
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
    })
    AsyncStorage.removeItem(STORAGE_KEY).catch(() => {})
  },

  hydrate: async () => {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed?.token && parsed?.user) {
          set({
            user: parsed.user,
            token: parsed.token,
            refreshToken: parsed.refreshToken || null,
            isAuthenticated: true,
            isHydrated: true,
          })
          return
        }
      }
    } catch {
      // Ignore corrupted storage
    } finally {
      set({ isHydrated: true })
    }
  },
}))

