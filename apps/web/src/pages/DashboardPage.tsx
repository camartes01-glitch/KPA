/**
 * Dashboard Page — Role-aware live summary dashboard connected to FastAPI.
 */
import { useEffect, useState } from 'react'
import {
  Users,
  UserCheck,
  Heart,
  CreditCard,
  TrendingUp,
  AlertCircle,
  Clock,
  Zap,
  RefreshCw,
  MapPin,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'

interface DistrictMetricItem {
  district_name: string
  total_members: number
  approved_members: number
  total_collected: number
  pending_dues: number
}

interface DashboardMetrics {
  total_members: number
  active_members: number
  pending_approvals: number
  active_welfare_events: number
  total_welfare_target: number
  total_collected_today: number
  total_collected_monthly: number
  total_pending_dues: number
  autopay_active_members: number
  district_breakdown?: DistrictMetricItem[] | null
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get('/dashboard/metrics')
      setMetrics(response.data.data)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      setError(msg || 'Failed to load dashboard metrics.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
  }, [])

  const statCards = [
    {
      label: 'Total Members',
      value: metrics ? metrics.total_members.toLocaleString() : '—',
      icon: Users,
      color: 'var(--color-primary-500)',
      subtext: `${metrics?.active_members ?? 0} active`,
    },
    {
      label: 'Pending Approvals',
      value: metrics ? metrics.pending_approvals.toLocaleString() : '—',
      icon: Clock,
      color: 'var(--color-warning-500)',
      subtext: 'KYC review queue',
    },
    {
      label: 'Active Welfare Events',
      value: metrics ? metrics.active_welfare_events.toLocaleString() : '—',
      icon: Heart,
      color: 'var(--color-error-500)',
      subtext: metrics ? `₹${metrics.total_welfare_target.toLocaleString('en-IN')} target` : '—',
    },
    {
      label: "Today's Collection",
      value: metrics ? `₹${metrics.total_collected_today.toLocaleString('en-IN')}` : '—',
      icon: CreditCard,
      color: 'var(--color-gold-400)',
      subtext: 'Settled UPI / Gateway',
    },
    {
      label: 'Monthly Collection',
      value: metrics ? `₹${metrics.total_collected_monthly.toLocaleString('en-IN')}` : '—',
      icon: TrendingUp,
      color: 'var(--color-primary-700)',
      subtext: 'Calendar month',
    },
    {
      label: 'Pending Dues',
      value: metrics ? `₹${metrics.total_pending_dues.toLocaleString('en-IN')}` : '—',
      icon: AlertCircle,
      color: 'var(--color-error-400)',
      subtext: 'Uncollected debits',
    },
    {
      label: 'AutoPay Mandates',
      value: metrics ? metrics.autopay_active_members.toLocaleString() : '—',
      icon: Zap,
      color: 'var(--color-success-500)',
      subtext: 'Recurring debit active',
    },
    {
      label: 'Active Ratio',
      value:
        metrics && metrics.total_members > 0
          ? `${Math.round((metrics.active_members / metrics.total_members) * 100)}%`
          : '—',
      icon: UserCheck,
      color: 'var(--color-primary-600)',
      subtext: 'Member compliance',
    },
  ]

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 'var(--space-6)',
          flexWrap: 'wrap',
          gap: 'var(--space-4)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>Dashboard</h1>
            <span
              style={{
                background: 'var(--color-primary-100)',
                color: 'var(--color-primary-800)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <MapPin size={12} />
              {user?.role?.replace('_', ' ')}
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Welcome back, <strong>{user?.name || user?.email || user?.phone || 'User'}</strong>. Real-time metrics from the KPA Welfare Engine.
          </p>
        </div>

        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="btn btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div
          className="card"
          style={{
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            marginBottom: 'var(--space-6)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-3)',
          }}
        >
          <AlertCircle size={20} color="var(--color-error-500)" />
          <span style={{ color: 'var(--color-error-500)', fontSize: 'var(--font-size-sm)' }}>{error}</span>
        </div>
      )}

      {/* Stat grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-8)',
        }}
      >
        {statCards.map(({ label, value, icon: Icon, color, subtext }) => (
          <div key={label} className="stat-card">
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 'var(--space-3)',
              }}
            >
              <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>
                {label}
              </span>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 'var(--radius-md)',
                  background: `${color}18`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Icon size={18} style={{ color }} />
              </div>
            </div>
            <div
              style={{
                fontSize: 'var(--font-size-3xl)',
                fontWeight: 800,
                color: 'var(--text-primary)',
                letterSpacing: '-0.02em',
              }}
            >
              {loading && !metrics ? '...' : value}
            </div>
            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
              {subtext}
            </div>
          </div>
        ))}
      </div>

      {/* District breakdown table for State Head */}
      {metrics?.district_breakdown && metrics.district_breakdown.length > 0 && (
        <div className="card" style={{ marginBottom: 'var(--space-8)' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 'var(--space-4)',
              borderBottom: '1px solid var(--border-default)',
              paddingBottom: 'var(--space-3)',
            }}
          >
            <div>
              <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, margin: 0 }}>
                District Geographic Breakdown
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', marginTop: 2 }}>
                Karnataka State Overview — Member registrations and welfare collections by district
              </p>
            </div>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-default)', textAlign: 'left' }}>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>District</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Total Members</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Approved</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Total Collected</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Pending Dues</th>
                </tr>
              </thead>
              <tbody>
                {metrics.district_breakdown.map((d) => (
                  <tr
                    key={d.district_name}
                    style={{ borderBottom: '1px solid var(--border-default)' }}
                  >
                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontWeight: 600 }}>
                      {d.district_name}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>{d.total_members}</td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <span
                        style={{
                          background: 'rgba(16, 185, 129, 0.12)',
                          color: '#059669',
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-full)',
                          fontSize: 'var(--font-size-xs)',
                          fontWeight: 600,
                        }}
                      >
                        {d.approved_members}
                      </span>
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontWeight: 600, color: 'var(--color-primary-700)' }}>
                      ₹{d.total_collected.toLocaleString('en-IN')}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: d.pending_dues > 0 ? 'var(--color-error-500)' : 'var(--text-muted)' }}>
                      ₹{d.pending_dues.toLocaleString('en-IN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
