/**
 * Dashboard Page — role-aware summary dashboard.
 * Will display real data from the API in Phase 9.
 * Placeholder stat cards shown for now with loading state.
 */
import { Users, UserCheck, Heart, CreditCard, TrendingUp, AlertCircle } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

const statCards = [
  { label: 'Total Members',    value: '—', icon: Users,       color: 'var(--color-primary-500)' },
  { label: 'Active Members',   value: '—', icon: UserCheck,   color: 'var(--color-success-500)' },
  { label: 'Welfare Events',   value: '—', icon: Heart,       color: 'var(--color-error-500)' },
  { label: "Today's Collection", value: '—', icon: CreditCard, color: 'var(--color-gold-400)' },
  { label: 'Monthly Collection', value: '—', icon: TrendingUp, color: 'var(--color-primary-700)' },
  { label: 'Pending Dues',     value: '—', icon: AlertCircle, color: 'var(--color-warning-500)' },
]

export default function DashboardPage() {
  const { user } = useAuthStore()

  return (
    <div>
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
          Welcome back, <strong>{user?.name}</strong> — {user?.role?.replace('_', ' ')}
        </p>
      </div>

      {/* Stat grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-8)',
      }}>
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
              <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>
                {label}
              </span>
              <div style={{
                width: 36,
                height: 36,
                borderRadius: 'var(--radius-md)',
                background: `${color}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <Icon size={18} style={{ color }} />
              </div>
            </div>
            <div style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
              {value}
            </div>
            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
              Live data available after Phase 9
            </div>
          </div>
        ))}
      </div>

      {/* Placeholder notice */}
      <div className="card" style={{ background: 'var(--color-primary-50)', border: '1px solid var(--color-primary-200)' }}>
        <p style={{ color: 'var(--color-primary-700)', fontWeight: 500 }}>
          📊 Phase 1 Foundation — Dashboard analytics and charts will be populated in Phase 9.
          Authentication, member management, welfare events, and payments are being built in Phases 2–8.
        </p>
      </div>
    </div>
  )
}
