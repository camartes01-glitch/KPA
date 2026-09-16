/**
 * Welfare Events Page — Active relief events, member contribution tracking, and relief case declaration.
 */
import { useEffect, useState } from 'react'
import {
  Heart,
  RefreshCw,
  Plus,
  Eye,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface WelfareEventItem {
  id: string
  title: string
  deceased_member_id: string
  cause_of_death?: string | null
  death_date: string
  target_amount: number
  collected_amount: number
  status: 'ACTIVE' | 'CLOSED' | 'SETTLED' | string
  created_at: string
}

interface MemberOption {
  id: string
  membership_no?: string
  full_name: string
  phone?: string
  status: string
}

interface ContributionDetail {
  contribution_id: string
  member_id: string
  member_name: string
  membership_no?: string | null
  amount: number
  status: string
  paid_at?: string | null
  payment_method?: string | null
}

interface EventBreakdown {
  event_id: string
  event_title: string
  status: string
  target_amount: number
  collected_amount: number
  pending_amount: number
  collection_percentage: number
  total_obligated_members: number
  paid_count: number
  unpaid_count: number
  contributions: ContributionDetail[]
}

export default function WelfareEventsPage() {
  const { user } = useAuthStore()
  const [events, setEvents] = useState<WelfareEventItem[]>([])
  const [loading, setLoading] = useState(true)

  // Declare Modal
  const [showDeclareModal, setShowDeclareModal] = useState(false)
  const [approvedMembers, setApprovedMembers] = useState<MemberOption[]>([])
  const [selectedMemberId, setSelectedMemberId] = useState('')
  const [caseTitle, setCaseTitle] = useState('')
  const [deathDate, setDeathDate] = useState('')
  const [causeOfDeath, setCauseOfDeath] = useState('')
  const [certificateUrl, setCertificateUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Breakdown Modal
  const [activeBreakdown, setActiveBreakdown] = useState<EventBreakdown | null>(null)
  const [loadingBreakdown, setLoadingBreakdown] = useState(false)

  const isStateHead = user?.role === 'STATE_HEAD'

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await api.get('/welfare-events')
      setEvents(res.data.data || [])
    } catch {
      toast.error('Failed to load welfare events')
    } finally {
      setLoading(false)
    }
  }

  const loadApprovedMembers = async () => {
    try {
      const res = await api.get('/members', { params: { status: 'APPROVED', page_size: 100 } })
      setApprovedMembers(res.data.data || [])
    } catch {
      toast.error('Failed to load member directory for selection')
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleOpenDeclareModal = () => {
    setShowDeclareModal(true)
    loadApprovedMembers()
    setDeathDate(new Date().toISOString().split('T')[0])
  }

  const handleMemberSelect = (memberId: string) => {
    setSelectedMemberId(memberId)
    const m = approvedMembers.find((mem) => mem.id === memberId)
    if (m) {
      setCaseTitle(`Bereavement & Family Emergency Relief for Late ${m.full_name}`)
    }
  }

  const handleDeclareEvent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedMemberId) {
      toast.warn('Please select a deceased member.')
      return
    }

    setSubmitting(true)
    try {
      await api.post('/welfare-events', {
        deceased_member_id: selectedMemberId,
        title: caseTitle,
        death_date: deathDate,
        cause_of_death: causeOfDeath || undefined,
        death_certificate_url: certificateUrl || undefined,
      })
      toast.success('Welfare event declared! Mutual ₹10 obligations generated statewide.')
      setShowDeclareModal(false)
      setSelectedMemberId('')
      setCaseTitle('')
      setCauseOfDeath('')
      setCertificateUrl('')
      fetchData()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg || 'Failed to declare welfare event')
    } finally {
      setSubmitting(false)
    }
  }

  const viewEventBreakdown = async (eventId: string) => {
    setLoadingBreakdown(true)
    try {
      const res = await api.get(`/welfare-events/${eventId}/contributions`)
      setActiveBreakdown(res.data.data)
    } catch {
      toast.error('Failed to fetch event contributions breakdown')
    } finally {
      setLoadingBreakdown(false)
    }
  }

  return (
    <div>
      {/* Header */}
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
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>
            Welfare Relief Cases
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Statewide mutual relief distributions, ₹10 levy collections, and death benefit disbursements.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          {isStateHead && (
            <button
              onClick={handleOpenDeclareModal}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
            >
              <Plus size={16} />
              Declare Welfare Event
            </button>
          )}
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

      {/* Welfare Events Grid */}
      {loading ? (
        <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
          <p>Loading welfare relief events...</p>
        </div>
      ) : events.length === 0 ? (
        <div className="card" style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Heart size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-error-500)', opacity: 0.4 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            No Active Welfare Relief Cases
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            When a bereavement or emergency relief case is declared by the State Head, statewide ₹10 member debits are generated automatically.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 'var(--space-5)' }}>
          {events.map((ev) => {
            const target = Number(ev.target_amount) || 0
            const collected = Number(ev.collected_amount) || 0
            const percent = target > 0 ? Math.min(100, Math.round((collected / target) * 100)) : 0

            return (
              <div key={ev.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-2)' }}>
                  <div>
                    <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                      {ev.title}
                    </h3>
                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
                      Demise Date: {ev.death_date} • Registered: {new Date(ev.created_at).toLocaleDateString('en-IN')}
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

                {ev.cause_of_death && (
                  <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0 }}>
                    <strong>Cause of Demise:</strong> {ev.cause_of_death}
                  </p>
                )}

                {/* Progress Bar & Financials */}
                <div style={{ marginTop: 'auto', paddingTop: 'var(--space-2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-xs)', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>
                      Collected: <strong style={{ color: '#059669' }}>₹{collected.toLocaleString('en-IN')}</strong>
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>
                      Target: ₹{target.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div style={{ width: '100%', height: 8, background: 'var(--bg-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${percent}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, var(--color-primary-600), var(--color-gold-500))',
                        borderRadius: 'var(--radius-full)',
                        transition: 'width 0.4s ease',
                      }}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6, fontSize: 'var(--font-size-xs)' }}>
                    <span style={{ color: 'var(--text-muted)' }}>₹10 per active member</span>
                    <span style={{ fontWeight: 800, color: 'var(--color-primary-700)' }}>{percent}% Collected</span>
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--border-default)', paddingTop: 'var(--space-3)', display: 'flex', justifyContent: 'flex-end' }}>
                  <button
                    onClick={() => viewEventBreakdown(ev.id)}
                    disabled={loadingBreakdown}
                    className="btn btn-secondary"
                    style={{ fontSize: 'var(--font-size-xs)', display: 'flex', alignItems: 'center', gap: 6 }}
                  >
                    <Eye size={14} />
                    {loadingBreakdown ? 'Loading...' : 'View Member Ledgers'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Declare Welfare Event Modal */}
      {showDeclareModal && (
        <div className="modal-backdrop">
          <div className="modal" style={{ maxWidth: 540 }}>
            <h3 style={{ margin: '0 0 var(--space-4)' }}>Declare Welfare Relief Case</h3>
            <form onSubmit={handleDeclareEvent} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div>
                <label className="label">Select Deceased Member (Approved Members Only)</label>
                <select
                  required
                  className="input"
                  value={selectedMemberId}
                  onChange={(e) => handleMemberSelect(e.target.value)}
                >
                  <option value="">Choose member...</option>
                  {approvedMembers.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.full_name} ({m.membership_no || 'No ID'}) - {m.phone || 'No phone'}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Event Title / Description</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. Emergency Death Relief for Late Ramesh"
                  value={caseTitle}
                  onChange={(e) => setCaseTitle(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <div>
                  <label className="label">Date of Demise</label>
                  <input
                    type="date"
                    required
                    className="input"
                    value={deathDate}
                    onChange={(e) => setDeathDate(e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">Cause of Demise (Optional)</label>
                  <input
                    className="input"
                    placeholder="e.g. Cardiac arrest, accident"
                    value={causeOfDeath}
                    onChange={(e) => setCauseOfDeath(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="label">Death Certificate / Proof URL (Optional)</label>
                <input
                  type="url"
                  className="input"
                  placeholder="https://storage.../certificate.pdf"
                  value={certificateUrl}
                  onChange={(e) => setCertificateUrl(e.target.value)}
                />
              </div>

              <div style={{ background: 'var(--color-primary-50)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-xs)', color: 'var(--color-primary-800)' }}>
                <strong>Automated Statewide Settlement Rule:</strong>
                <p style={{ margin: '4px 0 0' }}>
                  Upon declaration, the backend automatically debits exactly ₹10 from all active verified members statewide into an emergency escrow relief pool.
                </p>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
                <button type="button" onClick={() => setShowDeclareModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn btn-primary">
                  {submitting ? 'Declaring...' : 'Declare & Dispatch Alerts'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Member Contributions Breakdown Modal */}
      {activeBreakdown && (
        <div className="modal-backdrop">
          <div className="modal" style={{ maxWidth: 680, maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
              <div>
                <h3 style={{ margin: 0 }}>{activeBreakdown.event_title}</h3>
                <p style={{ margin: 0, fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                  Statewide Member Ledger & Settlement Breakdown
                </p>
              </div>
              <button
                onClick={() => setActiveBreakdown(null)}
                style={{ border: 'none', background: 'transparent', cursor: 'pointer', fontSize: 18, color: 'var(--text-muted)' }}
              >
                ✕
              </button>
            </div>

            {/* Metrics Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
              <div style={{ background: 'var(--bg-subtle)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Target Relief</div>
                <div style={{ fontSize: 16, fontWeight: 800 }}>₹{activeBreakdown.target_amount}</div>
              </div>
              <div style={{ background: 'var(--bg-subtle)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Collected (Paid)</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: '#059669' }}>₹{activeBreakdown.collected_amount}</div>
              </div>
              <div style={{ background: 'var(--bg-subtle)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Pending Dues</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: '#d97706' }}>₹{activeBreakdown.pending_amount}</div>
              </div>
              <div style={{ background: 'var(--bg-subtle)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Compliance</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--color-primary-700)' }}>
                  {activeBreakdown.collection_percentage}%
                </div>
              </div>
            </div>

            {/* Contributions List */}
            <div style={{ overflowY: 'auto', flex: 1, borderTop: '1px solid var(--border-default)' }}>
              <table className="table" style={{ width: '100%', fontSize: 'var(--font-size-xs)' }}>
                <thead>
                  <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-default)' }}>
                    <th style={{ padding: '8px 12px' }}>Member</th>
                    <th style={{ padding: '8px 12px' }}>Membership ID</th>
                    <th style={{ padding: '8px 12px' }}>Amount</th>
                    <th style={{ padding: '8px 12px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {activeBreakdown.contributions.map((c) => (
                    <tr key={c.contribution_id} style={{ borderBottom: '1px solid var(--border-default)' }}>
                      <td style={{ padding: '8px 12px', fontWeight: 600 }}>{c.member_name}</td>
                      <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>{c.membership_no || 'N/A'}</td>
                      <td style={{ padding: '8px 12px' }}>₹{c.amount}</td>
                      <td style={{ padding: '8px 12px' }}>
                        <span
                          style={{
                            fontWeight: 700,
                            color: c.status === 'SUCCESS' ? '#059669' : '#d97706',
                          }}
                        >
                          {c.status === 'SUCCESS' ? '● PAID' : '● PENDING'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
