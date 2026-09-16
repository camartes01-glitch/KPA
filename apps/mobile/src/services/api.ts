/**
 * Axios API client for KPA Mobile App.
 * Connects to FastAPI backend and handles JWT authentication with authStore.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../store/authStore'

const rawEnvUrl = process.env.EXPO_PUBLIC_API_URL

export const BASE_URL = (
  rawEnvUrl && rawEnvUrl.trim().length > 0
    ? rawEnvUrl.trim().replace(/\/+$/, '')
    : typeof __DEV__ !== 'undefined' && __DEV__
    ? 'http://localhost:8000/api/v1'
    : 'https://api.kpawelfare.org/api/v1'
)

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Translates technical API & Network errors into clear, user-friendly messages.
 * Detailed technical trace is logged only in development (__DEV__).
 */
export function getErrorMessage(error: unknown): string {
  if (__DEV__) {
    console.log('[API Error Debug]:', error)
  }

  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return 'Request timed out. Please check your internet connection and try again.'
    }

    if (!error.response) {
      return 'Unable to connect to KPA Welfare server. Please check your internet connection and try again.'
    }

    const status = error.response.status
    const backendMessage = error.response.data?.detail || error.response.data?.message

    if (typeof backendMessage === 'string' && backendMessage.trim().length > 0) {
      return backendMessage
    }

    if (status === 401) {
      return 'Session expired. Please log in again.'
    }

    if (status === 403) {
      return 'Access denied. You do not have permission for this action.'
    }

    if (status === 404) {
      return 'Requested information was not found on the server.'
    }

    if (status >= 500) {
      return 'Server is temporarily undergoing maintenance. Please try again later.'
    }
  }

  if (error instanceof Error && error.message) {
    if (error.message.toLowerCase().includes('network error')) {
      return 'Unable to connect to KPA Welfare server. Please check your internet connection and try again.'
    }
    return error.message
  }

  return 'An unexpected error occurred. Please check your connection and try again.'
}

// ── Request interceptor — attach access token ──────────────────────────────
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor — handle 401 and refresh token ────────────────────
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error)
    else prom.resolve(token!)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = useAuthStore.getState().refreshToken

      if (!refreshToken) {
        useAuthStore.getState().logout()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Contract matches backend POST /api/v1/auth/token/refresh
        const res = await axios.post(`${BASE_URL}/auth/token/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token: newRefreshToken, user } =
          res.data.data

        useAuthStore.getState().setAuth(user, access_token, newRefreshToken)
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
 * Health check helper to test connectivity from mobile device to FastAPI backend.
 */
export async function checkBackendHealth(): Promise<{
  ok: boolean
  data?: any
  error?: string
}> {
  try {
    const healthPath = BASE_URL.endsWith('/api/v1')
      ? BASE_URL.replace(/\/api\/v1$/, '/health')
      : `${BASE_URL}/health`
    const res = await axios.get(healthPath, { timeout: 5000 })
    return { ok: true, data: res.data }
  } catch (err: any) {
    return { ok: false, error: getErrorMessage(err) }
  }
}

export default api
