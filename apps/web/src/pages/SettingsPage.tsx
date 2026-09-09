/**
 * Settings Page — Association configuration, payment gateways, notifications, and language settings.
 */
import { Globe, Shield, Sliders } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div>
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Association Settings</h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
          Global platform configurations, welfare calculation rules, notifications, and integrations.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: 'var(--space-4)',
      }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
            <Globe size={20} style={{ color: 'var(--color-primary-500)' }} />
            <h4 style={{ margin: 0, fontWeight: 600 }}>Language & Localization</h4>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0 }}>
            English & Kannada (ಕನ್ನಡ) language switcher, localized date-time formatting, and notification templates.
          </p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
            <Shield size={20} style={{ color: 'var(--color-success-500)' }} />
            <h4 style={{ margin: 0, fontWeight: 600 }}>Security & Sessions</h4>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0 }}>
            Device session limits, OTP cooldown durations, rate limits, and audit preservation policies.
          </p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
            <Sliders size={20} style={{ color: 'var(--color-gold-500)' }} />
            <h4 style={{ margin: 0, fontWeight: 600 }}>Welfare Fund Rules</h4>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0 }}>
            Nominee eligibility rules, default per-member contribution amounts, and grace period thresholds.
          </p>
        </div>
      </div>
    </div>
  )
}
