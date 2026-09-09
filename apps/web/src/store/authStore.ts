/**
 * Auth store — manages authentication state in memory + localStorage.
 * Token storage uses localStorage for the web admin.
 * Actual token validation is always server-side.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type UserRole = 'STATE_HEAD' | 'DISTRICT_ADMIN' | 'TALUKA_ADMIN' | 'MEMBER'

export interface AuthUser {
  id: string
  name: string
  mobile: string
  role: UserRole
  districtId?: string
  talukaId?: string
}

interface AuthState {
  isAuthenticated: boolean
  user: AuthUser | null
  accessToken: string | null
  refreshToken: string | null
  setAuth: (user: AuthUser, accessToken: string, refreshToken: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, accessToken, refreshToken) =>
        set({ isAuthenticated: true, user, accessToken, refreshToken }),
      logout: () =>
        set({ isAuthenticated: false, user: null, accessToken: null, refreshToken: null }),
    }),
    {
      name: 'kpa-auth',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
)
