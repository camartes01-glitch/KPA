/**
 * Login Page — Google OAuth 2.0 Single Sign-On.
 * Replaces mobile OTP with Google Identity Services.
 */
import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const googleBtnRef = useRef<HTMLDivElement>(null)

  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const rawClientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || '').trim()
  const isConfigured = Boolean(
    rawClientId &&
      !rawClientId.includes('YOUR_GOOGLE_CLIENT_ID') &&
      !rawClientId.startsWith('<')
  )

  const handleGoogleCredentialResponse = async (response: { credential: string }) => {
    if (!response?.credential) {
      toast.error('No credential received from Google.')
      return
    }

    setLoading(true)
    setErrorMessage(null)
    try {
      const res = await api.post('/auth/google', {
        id_token: response.credential,
      })

      const { user, access_token, refresh_token } = res.data.data
      setAuth(user, access_token, refresh_token)
      toast.success(`Welcome, ${user.name || user.email}!`)
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string; message?: string } } })?.response?.data?.detail ||
        (err as { response?: { data?: { detail?: string; message?: string } } })?.response?.data?.message ||
        'Google authentication failed. Please try again.'
      setErrorMessage(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!isConfigured) return

    const initGsi = () => {
      if (window.google?.accounts?.id && googleBtnRef.current) {
        try {
          window.google.accounts.id.initialize({
            client_id: rawClientId,
            callback: handleGoogleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true,
          })

          googleBtnRef.current.innerHTML = ''
          window.google.accounts.id.renderButton(googleBtnRef.current, {
            theme: 'outline',
            size: 'large',
            text: 'continue_with',
            shape: 'rectangular',
            width: 340,
            logo_alignment: 'left',
          })
        } catch (e) {
          console.error('Failed to initialize Google Sign-In button', e)
        }
      }
    }

    if (window.google?.accounts?.id) {
      initGsi()
    } else {
      const timer = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(timer)
          initGsi()
        }
      }, 200)
      return () => clearInterval(timer)
    }
  }, [isConfigured, rawClientId])

  return (
    <div
      style={{
        minHeight: '100vh',
        background:
          'linear-gradient(135deg, var(--color-primary-900) 0%, var(--color-primary-700) 60%, var(--color-primary-500) 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-4)',
      }}
    >
      <div
        style={{
          background: 'var(--bg-surface)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-10)',
          width: '100%',
          maxWidth: 420,
          boxShadow: 'var(--shadow-xl)',
          textAlign: 'center',
        }}
      >
        {/* Logo */}
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <div
            style={{
              width: 72,
              height: 72,
              background: 'linear-gradient(135deg, var(--color-primary-700), var(--color-primary-500))',
              borderRadius: 'var(--radius-xl)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto var(--space-4)',
              boxShadow: '0 8px 24px rgba(26,58,107,0.4)',
            }}
          >
            <span style={{ fontSize: 32 }}>📷</span>
          </div>
          <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, color: 'var(--color-primary-700)' }}>
            KPA Welfare
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', marginTop: 4 }}>
            Karnataka Photography Association
          </p>
        </div>

        <div style={{ marginBottom: 'var(--space-6)', textAlign: 'left' }}>
          <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 4 }}>
            Sign In with Google
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>
            Please use your registered Google account (@gmail.com) to access the welfare management portal.
          </p>
        </div>

        {errorMessage && (
          <div
            id="login-error-banner"
            style={{
              padding: 'var(--space-3)',
              marginBottom: 'var(--space-4)',
              borderRadius: 'var(--radius-md)',
              background: '#fee2e2',
              border: '1px solid #ef4444',
              color: '#b91c1c',
              fontSize: 'var(--font-size-sm)',
              textAlign: 'left',
            }}
          >
            {errorMessage}
          </div>
        )}

        {/* Google Identity Services Container */}
        <div style={{ minHeight: 48, display: 'flex', justifyContent: 'center', marginBottom: 'var(--space-4)' }}>
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary-700)' }}>
              <span className="spinner" style={{ width: 22, height: 22 }} />
              <span>Verifying account with Google...</span>
            </div>
          ) : isConfigured ? (
            <div ref={googleBtnRef} id="google-signin-btn" />
          ) : (
            <div
              id="oauth-client-id-required-notice"
              style={{
                background: '#f8fafc',
                border: '1px dashed #cbd5e1',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-4)',
                width: '100%',
                fontSize: 'var(--font-size-xs)',
                color: 'var(--text-secondary)',
                lineHeight: 1.5,
              }}
            >
              <strong style={{ color: 'var(--color-primary-700)', display: 'block', marginBottom: 4 }}>
                OAuth Client ID Required
              </strong>
              Configure <code style={{ color: '#0f172a' }}>VITE_GOOGLE_CLIENT_ID</code> in <code style={{ color: '#0f172a' }}>apps/web/.env</code> to activate the Google Sign-In button.
            </div>
          )}
        </div>

        <div
          style={{
            marginTop: 'var(--space-6)',
            paddingTop: 'var(--space-4)',
            borderTop: '1px solid var(--border-default)',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--text-muted)',
            lineHeight: 1.6,
          }}
        >
          <span>Official member & administrator portal. Protected by Google Identity Services and KPA Role-Based Access Control.</span>
        </div>
      </div>
    </div>
  )
}
