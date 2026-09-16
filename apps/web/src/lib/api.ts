/**
 * Axios API client with JWT interceptor, automatic token refresh,
 * and centralized production error handling.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

export const BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : 'https://api.kpawelfare.org/api/v1')

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor — attach access token ────────────────────────────────
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor — handle 401 + token refresh & error normalization ──
let isRefreshing = false
let failedQueue: Array<{ resolve: (v: string) => void; reject: (e: unknown) => void }> = []

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((p) => {
    if (error) p.reject(error)
    else p.resolve(token!)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
      _retryCount?: number
    }

    // 1. Handle 401 Unauthorized with token refresh rotation
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1
      if (originalRequest._retryCount > 2) {
        useAuthStore.getState().logout()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = useAuthStore.getState().refreshToken

      if (!refreshToken) {
        useAuthStore.getState().logout()
        return Promise.reject(error)
      }

      try {
        const response = await axios.post(`${BASE_URL}/auth/token/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token } = response.data.data
        const { user } = useAuthStore.getState()
        useAuthStore.getState().setAuth(user!, access_token, refresh_token)
        processQueue(null, access_token)
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        useAuthStore.getState().logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

/**
 * Normalizes backend error responses (FastAPI detail, error message, or network error)
 * into a user-friendly string for UI alerts and toast notifications.
 */
export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const data = error.response?.data as any

    if (!error.response) {
      return 'Unable to connect to KPA server. Please check your internet connection.'
    }

    if (data) {
      // 422 validation error
      if (status === 422 && Array.isArray(data.detail)) {
        return data.detail.map((err: any) => err.msg || `${err.loc?.join('.')} is invalid`).join(', ')
      }
      if (data.detail && typeof data.detail === 'string') {
        return data.detail
      }
      if (data.message && typeof data.message === 'string') {
        return data.message
      }
    }

    switch (status) {
      case 401:
        return 'Session expired. Please log in again.'
      case 403:
        return 'You do not have permission to perform this action.'
      case 404:
        return 'The requested resource was not found.'
      case 409:
        return 'A conflict occurred with the current state of the resource.'
      case 429:
        return 'Too many requests. Please wait a moment and try again.'
      case 500:
        return 'An internal server error occurred. Please contact system support.'
      default:
        return error.message || 'An unexpected error occurred.'
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred.'
}

export default api
