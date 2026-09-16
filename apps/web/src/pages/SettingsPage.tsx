/**
 * Settings Page — Association Configuration, Welfare Rules, Provider Health, and Security Policies.
 */
import { useState, useEffect } from 'react'
import {
  Sliders,
  CheckCircle2,
  AlertCircle,
  Save,
  RefreshCw,
  Building,
  CreditCard,
  MessageSquare,
  Mail,
  Smartphone,
  Lock,
} from 'lucide-react'
import { api, extractErrorMessage } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

interface PlatformSettings {
  association_name: string
  association_name_kn: string
  association_address: string
  contact_phone: string
  contact_email: string
  welfare_contribution_inr: number
  welfare_grace_days: number
  providers: {
    razorpay_configured: boolean
    sms_configured: boolean
    email_configured: boolean
    push_configured: boolean
  }
  security: {
    jwt_access_expire_minutes: number
    jwt_refresh_expire_days: number
    otp_expiry_minutes: number
    otp_dev_mode: boolean
    app_env: string
  }
}

export default function SettingsPage() {
  const { user } = useAuthStore()
  const isStateHead = user?.role === 'STATE_HEAD'

  const [settingsData, setSettingsData] = useState<PlatformSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Form fields
  const [assocName, setAssocName] = useState('')
  const [assocNameKn, setAssocNameKn] = useState('')
  const [assocAddress, setAssocAddress] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [contributionInr, setContributionInr] = useState('10.00')
  const [graceDays, setGraceDays] = useState('14')

  const fetchSettings = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/settings')
      if (res.data?.success) {
        const d: PlatformSettings = res.data.data
        setSettingsData(d)
        setAssocName(d.association_name)
        setAssocNameKn(d.association_name_kn)
        setAssocAddress(d.association_address)
        setPhone(d.contact_phone)
        setEmail(d.contact_email)
        setContributionInr(String(d.welfare_contribution_inr))
        setGraceDays(String(d.welfare_grace_days))
      }
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isStateHead) return

    setSaving(true)
    setError(null)
    setSuccessMsg(null)

    try {
      const payload = {
        association_name: assocName.trim(),
        association_name_kn: assocNameKn.trim(),
        association_address: assocAddress.trim(),
        contact_phone: phone.trim(),
        contact_email: email.trim(),
        welfare_contribution_inr: parseFloat(contributionInr),
        welfare_grace_days: parseInt(graceDays, 10),
      }

      const res = await api.patch('/settings', payload)
      if (res.data?.success) {
        setSuccessMsg('Platform settings successfully updated and audited.')
        fetchSettings()
      }
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Platform Settings</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Association profile, welfare mutual fund rules, provider connectivity, and security configuration.
          </p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={fetchSettings}
          disabled={loading}
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Reload
        </button>
      </div>

      {/* Notifications */}
      {error && (
        <div className="card" style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: 'var(--color-danger-500)', marginBottom: 'var(--space-6)' }}>
          <p style={{ color: 'var(--color-danger-500)', margin: 0 }}>{error}</p>
        </div>
      )}
      {successMsg && (
        <div className="card" style={{ background: 'rgba(16, 185, 129, 0.1)', borderColor: 'var(--color-success-500)', marginBottom: 'var(--space-6)' }}>
          <p style={{ color: 'var(--color-success-500)', margin: 0 }}>{successMsg}</p>
        </div>
      )}

      {/* Provider Connectivity Status Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-6)',
      }}>
        {/* Razorpay */}
        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <CreditCard size={18} style={{ color: 'var(--color-gold-400)' }} />
              <strong style={{ fontSize: 'var(--font-size-sm)' }}>Razorpay Gateway</strong>
            </div>
            {settingsData?.providers.razorpay_configured ? (
              <span className="badge badge-success"><CheckCircle2 size={12} /> Active</span>
            ) : (
              <span className="badge badge-warning"><AlertCircle size={12} /> Sandbox</span>
            )}
          </div>
          <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)', margin: 0 }}>
            {settingsData?.providers.razorpay_configured
              ? 'Official production keys active. UPI & AutoPay enabled.'
              : 'Test mode active. Safe HMAC simulation enabled.'}
          </p>
        </div>

        {/* SMS (MSG91) */}
        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <MessageSquare size={18} style={{ color: 'var(--color-primary-400)' }} />
              <strong style={{ fontSize: 'var(--font-size-sm)' }}>SMS Gateway (MSG91)</strong>
            </div>
            {settingsData?.providers.sms_configured ? (
              <span className="badge badge-success"><CheckCircle2 size={12} /> Active</span>
            ) : (
              <span className="badge badge-warning"><AlertCircle size={12} /> Dev Mode</span>
            )}
          </div>
          <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)', margin: 0 }}>
            {settingsData?.providers.sms_configured
              ? 'DLT approved templates active for India SMS.'
              : 'Local OTP dev mode fallback active.'}
          </p>
        </div>

        {/* Email */}
        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Mail size={18} style={{ color: 'var(--color-info-400)' }} />
              <strong style={{ fontSize: 'var(--font-size-sm)' }}>Email Provider</strong>
            </div>
            {settingsData?.providers.email_configured ? (
              <span className="badge badge-success"><CheckCircle2 size={12} /> Active</span>
            ) : (
              <span className="badge badge-warning"><AlertCircle size={12} /> Local Mock</span>
            )}
          </div>
          <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)', margin: 0 }}>
            {settingsData?.providers.email_configured
              ? 'SendGrid / Resend API active for receipts & notices.'
              : 'Standard console logging active.'}
          </p>
        </div>

        {/* Push Notifications */}
        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Smartphone size={18} style={{ color: 'var(--color-success-400)' }} />
              <strong style={{ fontSize: 'var(--font-size-sm)' }}>Push (Expo/FCM)</strong>
            </div>
            {settingsData?.providers.push_configured ? (
              <span className="badge badge-success"><CheckCircle2 size={12} /> Active</span>
            ) : (
              <span className="badge badge-warning"><AlertCircle size={12} /> In-App DB</span>
            )}
          </div>
          <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)', margin: 0 }}>
            {settingsData?.providers.push_configured
              ? 'Firebase Cloud Messaging / Expo service linked.'
              : 'Database persistence active for mobile app.'}
          </p>
        </div>
      </div>

      {/* Main Settings Form */}
      <form onSubmit={handleSave}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-6)' }}>
          {/* Left Column: Association & Welfare Rules */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            {/* Association Profile */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 'var(--space-4)' }}>
                <Building size={20} style={{ color: 'var(--color-gold-400)' }} />
                <h3 style={{ margin: 0, fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>Association Profile</h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
                <div>
                  <label className="form-label">Association Name (English)</label>
                  <input
                    type="text"
                    className="form-control"
                    value={assocName}
                    onChange={(e) => setAssocName(e.target.value)}
                    disabled={!isStateHead || saving}
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Association Name (Kannada)</label>
                  <input
                    type="text"
                    className="form-control"
                    value={assocNameKn}
                    onChange={(e) => setAssocNameKn(e.target.value)}
                    disabled={!isStateHead || saving}
                    required
                  />
                </div>
              </div>

              <div style={{ marginBottom: 'var(--space-4)' }}>
                <label className="form-label">State Headquarters Address</label>
                <textarea
                  className="form-control"
                  rows={2}
                  value={assocAddress}
                  onChange={(e) => setAssocAddress(e.target.value)}
                  disabled={!isStateHead || saving}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <div>
                  <label className="form-label">Official Contact Phone</label>
                  <input
                    type="text"
                    className="form-control"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    disabled={!isStateHead || saving}
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Official Contact Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={!isStateHead || saving}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Welfare Mutual Fund Rules */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 'var(--space-4)' }}>
                <Sliders size={20} style={{ color: 'var(--color-primary-400)' }} />
                <h3 style={{ margin: 0, fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>Welfare Fund Rules</h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <div>
                  <label className="form-label">Per-Member Contribution Amount (₹)</label>
                  <input
                    type="number"
                    step="1.00"
                    min="1.00"
                    className="form-control"
                    value={contributionInr}
                    onChange={(e) => setContributionInr(e.target.value)}
                    disabled={!isStateHead || saving}
                    required
                  />
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                    Standard statutory relief deduction (default: ₹10.00).
                  </span>
                </div>

                <div>
                  <label className="form-label">Settlement Grace Period (Days)</label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    className="form-control"
                    value={graceDays}
                    onChange={(e) => setGraceDays(e.target.value)}
                    disabled={!isStateHead || saving}
                    required
                  />
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                    Allowed time window for member contribution settlement.
                  </span>
                </div>
              </div>
            </div>

            {isStateHead && (
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 24px' }}
                >
                  <Save size={16} />
                  {saving ? 'Saving...' : 'Save & Audit Changes'}
                </button>
              </div>
            )}
          </div>

          {/* Right Column: Security & Environment Info */}
          <div>
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 'var(--space-4)' }}>
                <Lock size={20} style={{ color: 'var(--color-success-400)' }} />
                <h3 style={{ margin: 0, fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>Security Policies</h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', fontSize: 'var(--font-size-sm)' }}>
                <div>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>ENVIRONMENT</span>
                  <span className="badge badge-primary">{settingsData?.security.app_env.toUpperCase() || 'DEVELOPMENT'}</span>
                </div>

                <div className="divider" style={{ margin: '4px 0' }} />

                <div>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>JWT ACCESS TOKEN LIFETIME</span>
                  <strong>{settingsData?.security.jwt_access_expire_minutes || 60} Minutes</strong>
                </div>

                <div>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>REFRESH TOKEN ROTATION</span>
                  <strong>{settingsData?.security.jwt_refresh_expire_days || 30} Days (Single-Use Rotation)</strong>
                </div>

                <div>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>OTP VALIDITY WINDOW</span>
                  <strong>{settingsData?.security.otp_expiry_minutes || 5} Minutes (Rate-Limited)</strong>
                </div>

                <div className="divider" style={{ margin: '4px 0' }} />

                <div>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>AUDIT PRESERVATION</span>
                  <strong>Immutable append-only ledger active across all 31 Districts</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  )
}
