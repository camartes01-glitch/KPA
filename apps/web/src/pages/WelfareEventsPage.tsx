/**
 * Welfare Events Page — Active relief events, member contribution tracking, and relief case initiation.
 */
import { useEffect, useState } from 'react'
import {
  Heart,
  RefreshCw,
  Clock,
  Check,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface WelfareEventItem {
  id: string
  title: string
  description?: string | null
  deceased_member_id?: string
  deceased_member_name?: string
  cause_of_death?: string | null
  death_date?: string | null
  target_amount: number
  collected_amount: number
  contribution_per_member?: number
  status: 'ACTIVE' | 'CLOSED' | 'SETTLED' | string
  created_at: string
}

interface ObligationItem {
  id?: string
  contribution_id?: string
  event_id: string
  event_title: string
  deceased_member_name?: string
  amount: number
  status: 'PENDING' | 'SUCCESS' | 'FAILED' | string
  payment_method?: string | null
  paid_at?: string | null
  created_at: string
}

export default function WelfareEventsPage() {
  const { user } = useAuthStore()
  const [events, setEvents] = useState<WelfareEventItem[]>([])
  const [obligations, setObligations] = useState<ObligationItem[]>([])
  const [loading, setLoading] = useState(true)

  const isMember = user?.role === 'MEMBER'

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await api.get('/welfare-events')
      setEvents(res.data.data || [])

      if (isMember) {
        try {
          const obRes = await api.get('/welfare-events/my-obligations')
          setObligations(obRes.data.data || [])
        } catch {
          // Member might not have a profile yet
        }
      }
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to load welfare events')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

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
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>Welfare Events</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Mutual relief funds, death benefit distributions, and photographer family support cases.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button
            onClick={fetchData}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Member Personal Obligations Card if user is MEMBER */}
      {isMember && (
        <div className="card" style={{ marginBottom: 'var(--space-6)', borderLeft: '4px solid var(--color-primary-500)' }}>
          <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, marginBottom: 'var(--space-3)' }}>
            My Mutual Welfare Obligations
          </h3>
          {obligations.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)', margin: 0 }}>
              No outstanding welfare debits at this time. All contributions are up to date!
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {obligations.map((ob) => (
                <div
                  key={ob.contribution_id || ob.id || ob.event_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-3)',
                    background: 'var(--bg-subtle)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--font-size-sm)' }}>{ob.event_title}</div>
                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                      Amount: ₹{ob.amount} • Debit on: {new Date(ob.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <span
                    style={{
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      background: ob.status === 'SUCCESS' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: ob.status === 'SUCCESS' ? '#059669' : '#d97706',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                    }}
                  >
                    {ob.status === 'SUCCESS' ? <Check size={12} /> : <Clock size={12} />}
                    {ob.status === 'SUCCESS' ? 'Contributed' : 'Pending Payment'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Welfare Events Grid */}
      {loading ? (
        <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
          <p>Loading welfare cases...</p>
        </div>
      ) : events.length === 0 ? (
        <div className="card" style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Heart size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-error-500)', opacity: 0.4 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            No Active Welfare Cases
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            When a bereavement or emergency relief case is approved by the State Head, member contributions will appear here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 'var(--space-4)' }}>
          {events.map((ev) => {
            const percent = ev.target_amount > 0 ? Math.min(100, Math.round((ev.collected_amount / ev.target_amount) * 100)) : 0

            return (
              <div key={ev.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-2)' }}>
                  <div>
                    <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                      {ev.title}
                    </h3>
                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
                      Case: <strong>{ev.deceased_member_name || ev.title}</strong>
                    </div>
                  </div>
                  <span
                    style={{
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      background: ev.status === 'ACTIVE' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.12)',
                      color: ev.status === 'ACTIVE' ? 'var(--color-error-600)' : '#059669',
                    }}
                  >
                    {ev.status}
                  </span>
                </div>

                {ev.description && (
                  <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0 }}>
                    {ev.description}
                  </p>
                )}

                {/* Progress Bar */}
                <div style={{ marginTop: 'auto', paddingTop: 'var(--space-2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-xs)', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Collected: <strong>₹{ev.collected_amount.toLocaleString('en-IN')}</strong></span>
                    <span style={{ color: 'var(--text-muted)' }}>Target: ₹{ev.target_amount.toLocaleString('en-IN')}</span>
                  </div>
                  <div style={{ width: '100%', height: 8, background: 'var(--bg-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${percent}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, var(--color-primary-500), var(--color-gold-500))',
                        borderRadius: 'var(--radius-full)',
                        transition: 'width 0.4s ease',
                      }}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6, fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                    <span>₹{ev.contribution_per_member} per member obligation</span>
                    <span style={{ fontWeight: 700, color: 'var(--color-primary-700)' }}>{percent}%</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
