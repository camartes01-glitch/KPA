/**
 * Login Page — mobile number + OTP authentication flow.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'react-toastify'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

const mobileSchema = z.object({
  mobile: z
    .string()
    .regex(/^[6-9]\d{9}$/, 'Enter a valid 10-digit Indian mobile number'),
})

const otpSchema = z.object({
  otp: z.string().length(6, 'OTP must be 6 digits').regex(/^\d+$/, 'OTP must be numeric'),
})

type MobileForm = z.infer<typeof mobileSchema>
type OtpForm = z.infer<typeof otpSchema>

export default function LoginPage() {
  const [step, setStep] = useState<'mobile' | 'otp'>('mobile')
  const [mobile, setMobile] = useState('')
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const mobileForm = useForm<MobileForm>({ resolver: zodResolver(mobileSchema) })
  const otpForm = useForm<OtpForm>({ resolver: zodResolver(otpSchema) })

  const handleRequestOtp = async (data: MobileForm) => {
    setLoading(true)
    try {
      await api.post('/auth/otp/send', { phone: data.mobile })
      setMobile(data.mobile)
      setStep('otp')
      toast.success('OTP sent successfully')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async (data: OtpForm) => {
    setLoading(true)
    try {
      const response = await api.post('/auth/otp/verify', {
        phone: mobile,
        otp: data.otp,
      })
      const { user, access_token, refresh_token } = response.data.data
      setAuth(user, access_token, refresh_token)
      toast.success(`Welcome back, ${user.name || 'User'}!`)
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Invalid OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickDemoLogin = async (phone: string) => {
    setLoading(true)
    try {
      await api.post('/auth/otp/send', { phone })
      setMobile(phone)
      const response = await api.post('/auth/otp/verify', {
        phone,
        otp: '123456',
      })
      const { user, access_token, refresh_token } = response.data.data
      setAuth(user, access_token, refresh_token)
      toast.success(`Logged in as ${user.name || user.role}`)
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Demo login failed. Ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, var(--color-primary-900) 0%, var(--color-primary-700) 60%, var(--color-primary-500) 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-4)',
    }}>
      <div style={{
        background: 'var(--bg-surface)',
        borderRadius: 'var(--radius-xl)',
        padding: 'var(--space-10)',
        width: '100%',
        maxWidth: 420,
        boxShadow: 'var(--shadow-xl)',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
          <div style={{
            width: 72,
            height: 72,
            background: 'linear-gradient(135deg, var(--color-primary-700), var(--color-primary-500))',
            borderRadius: 'var(--radius-xl)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto var(--space-4)',
            boxShadow: '0 8px 24px rgba(26,58,107,0.4)',
          }}>
            <span style={{ fontSize: 32 }}>📷</span>
          </div>
          <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, color: 'var(--color-primary-700)' }}>
            KPA Welfare
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', marginTop: 4 }}>
            Karnataka Photography Association
          </p>
        </div>

        {step === 'mobile' ? (
          <form onSubmit={mobileForm.handleSubmit(handleRequestOtp)}>
            <div style={{ marginBottom: 'var(--space-6)' }}>
              <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 4 }}>
                Sign In
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                Enter your registered mobile number
              </p>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="mobile">Mobile Number</label>
              <input
                id="mobile"
                className="form-input"
                type="tel"
                placeholder="9876543210"
                maxLength={10}
                {...mobileForm.register('mobile')}
              />
              {mobileForm.formState.errors.mobile && (
                <span className="form-error">
                  {mobileForm.formState.errors.mobile.message}
                </span>
              )}
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', justifyContent: 'center', padding: 'var(--space-3)' }}
            >
              {loading ? <span className="spinner" style={{ width: 18, height: 18 }} /> : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={otpForm.handleSubmit(handleVerifyOtp)}>
            <div style={{ marginBottom: 'var(--space-6)' }}>
              <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 4 }}>
                Enter OTP
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                OTP sent to <strong>+91 {mobile}</strong>
              </p>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="otp">One-Time Password</label>
              <input
                id="otp"
                className="form-input"
                type="text"
                inputMode="numeric"
                placeholder="123456"
                maxLength={6}
                style={{
                  fontSize: 'var(--font-size-2xl)',
                  letterSpacing: '0.3em',
                  textAlign: 'center',
                  fontWeight: 700,
                }}
                {...otpForm.register('otp')}
              />
              {otpForm.formState.errors.otp && (
                <span className="form-error">
                  {otpForm.formState.errors.otp.message}
                </span>
              )}
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', justifyContent: 'center', padding: 'var(--space-3)', marginBottom: 'var(--space-3)' }}
            >
              {loading ? <span className="spinner" style={{ width: 18, height: 18 }} /> : 'Verify & Login'}
            </button>

            <button
              type="button"
              onClick={() => setStep('mobile')}
              className="btn btn-secondary"
              style={{ width: '100%', justifyContent: 'center' }}
            >
              Change Number
            </button>
          </form>
        )}

        {/* Quick Demo Login Helper for Testing */}
        <div style={{ marginTop: 'var(--space-6)', paddingTop: 'var(--space-6)', borderTop: '1px solid var(--border-default)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
            <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-primary-600)' }}>
              Quick Demo Personas (Dev Mode)
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)' }}>
            <button
              type="button"
              id="demo-btn-state-head"
              disabled={loading}
              onClick={() => handleQuickDemoLogin('9900000001')}
              className="btn btn-secondary"
              style={{ fontSize: 'var(--font-size-xs)', padding: 'var(--space-2)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left' }}
            >
              <strong style={{ color: 'var(--color-primary-700)' }}>State Head</strong>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>9900000001</span>
            </button>
            <button
              type="button"
              id="demo-btn-district-admin"
              disabled={loading}
              onClick={() => handleQuickDemoLogin('9900000002')}
              className="btn btn-secondary"
              style={{ fontSize: 'var(--font-size-xs)', padding: 'var(--space-2)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left' }}
            >
              <strong style={{ color: 'var(--color-primary-700)' }}>District Admin</strong>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>BLR Urban</span>
            </button>
            <button
              type="button"
              id="demo-btn-taluka-admin"
              disabled={loading}
              onClick={() => handleQuickDemoLogin('9900000003')}
              className="btn btn-secondary"
              style={{ fontSize: 'var(--font-size-xs)', padding: 'var(--space-2)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left' }}
            >
              <strong style={{ color: 'var(--color-primary-700)' }}>Taluka Admin</strong>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>BLR North</span>
            </button>
            <button
              type="button"
              id="demo-btn-member"
              disabled={loading}
              onClick={() => handleQuickDemoLogin('9900000004')}
              className="btn btn-secondary"
              style={{ fontSize: 'var(--font-size-xs)', padding: 'var(--space-2)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left' }}
            >
              <strong style={{ color: 'var(--color-primary-700)' }}>Member</strong>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Prakash Hegde</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
