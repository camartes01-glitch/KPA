/**
 * Members Page — Directory, search, status filter, and KYC verification approvals.
 */
import { useEffect, useState, useCallback } from 'react'
import {
  Users,
  Search,
  CheckCircle,
  XCircle,
  Download,
  Filter,
  RefreshCw,
  AlertCircle,
  Building,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface MemberItem {
  id: string
  membership_no: string | null
  full_name: string
  father_or_spouse_name: string | null
  gender: string
  dob: string | null
  blood_group: string | null
  studio_name: string | null
  experience_years: number | null
  address_line: string | null
  district_id: string
  taluka_id: string
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'SUSPENDED'
  kyc_verified: boolean
  created_at: string
}

export default function MembersPage() {
  const { user } = useAuthStore()
  const [members, setMembers] = useState<MemberItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [totalPages, setTotalPages] = useState(1)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)

  const canApprove = user?.role === 'STATE_HEAD' || user?.role === 'DISTRICT_ADMIN'

  const fetchMembers = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
      }
      if (query.trim()) params.q = query.trim()
      if (statusFilter) params.member_status = statusFilter

      const response = await api.get('/members', { params })
      const data = response.data
      setMembers(data.data || [])
      setTotal(data.total || 0)
      setTotalPages(data.total_pages || 1)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to load member directory')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, query, statusFilter])

  useEffect(() => {
    fetchMembers()
  }, [fetchMembers])

  const handleApprove = async (memberId: string, name: string) => {
    if (!confirm(`Approve KYC & membership for "${name}"?`)) return
    setActionLoading(memberId)
    try {
      await api.post(`/members/${memberId}/approve`)
      toast.success(`Member "${name}" approved successfully`)
      fetchMembers()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to approve member')
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (memberId: string, name: string) => {
    const reason = prompt(`Enter rejection reason for "${name}":`, 'Incomplete KYC documents')
    if (!reason) return
    setActionLoading(memberId)
    try {
      await api.post(`/members/${memberId}/reject`, { reason })
      toast.info(`Member "${name}" rejected`)
      fetchMembers()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to reject member')
    } finally {
      setActionLoading(null)
    }
  }

  const handleExportCsv = async () => {
    setExporting(true)
    try {
      const response = await api.get('/reports/members/csv', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'kpa_members_export.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Member master roll downloaded')
    } catch {
      toast.error('Failed to export CSV report')
    } finally {
      setExporting(false)
    }
  }

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
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>Member Directory</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Manage KPA registered photographers, membership validation, and digital KYC approvals.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button
            onClick={handleExportCsv}
            disabled={exporting}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <Download size={16} />
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
          <button
            onClick={fetchMembers}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: 260, position: 'relative' }}>
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: 12,
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
              }}
            />
            <input
              type="text"
              placeholder="Search by name, membership ID, studio..."
              className="input"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setPage(1)
              }}
              style={{ paddingLeft: 40, width: '100%' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Filter size={16} color="var(--text-secondary)" />
            <select
              className="input"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              style={{ minWidth: 150 }}
            >
              <option value="">All Statuses</option>
              <option value="APPROVED">Approved</option>
              <option value="PENDING">Pending</option>
              <option value="REJECTED">Rejected</option>
              <option value="SUSPENDED">Suspended</option>
            </select>
          </div>

          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
            Total: <strong>{total}</strong> members
          </div>
        </div>
      </div>

      {/* Members Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
            <p>Loading members directory...</p>
          </div>
        ) : members.length === 0 ? (
          <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Users size={48} style={{ margin: '0 auto var(--space-4)', opacity: 0.4 }} />
            <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>No Members Found</h3>
            <p style={{ fontSize: 'var(--font-size-sm)' }}>
              {query || statusFilter
                ? 'No members match the active search or filter criteria.'
                : 'No members registered in this jurisdiction yet.'}
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border-default)', textAlign: 'left' }}>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Member</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Membership ID</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Studio / Experience</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Status</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>KYC</th>
                  {canApprove && (
                    <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'right' }}>Actions</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {members.map((m) => {
                  const isPending = m.status === 'PENDING'
                  const isApproved = m.status === 'APPROVED'

                  return (
                    <tr
                      key={m.id}
                      style={{ borderBottom: '1px solid var(--border-default)', transition: 'background 0.15s' }}
                    >
                      <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                          <div
                            style={{
                              width: 38,
                              height: 38,
                              borderRadius: 'var(--radius-full)',
                              background: 'var(--color-primary-100)',
                              color: 'var(--color-primary-800)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 700,
                              fontSize: 'var(--font-size-sm)',
                              flexShrink: 0,
                            }}
                          >
                            {m.full_name.charAt(0)}
                          </div>
                          <div>
                            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{m.full_name}</div>
                            {m.father_or_spouse_name && (
                              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                                c/o {m.father_or_spouse_name}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>

                      <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                        <span
                          style={{
                            fontFamily: 'monospace',
                            fontSize: 'var(--font-size-xs)',
                            fontWeight: 700,
                            background: m.membership_no ? 'rgba(37, 99, 235, 0.08)' : 'var(--bg-subtle)',
                            color: m.membership_no ? 'var(--color-primary-700)' : 'var(--text-muted)',
                            padding: '3px 8px',
                            borderRadius: 'var(--radius-sm)',
                          }}
                        >
                          {m.membership_no || 'PENDING'}
                        </span>
                      </td>

                      <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--font-size-sm)' }}>
                          <Building size={14} color="var(--text-muted)" />
                          <span>{m.studio_name || 'Individual'}</span>
                        </div>
                        {m.experience_years !== null && (
                          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                            {m.experience_years} yrs experience
                          </div>
                        )}
                      </td>

                      <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                        <span
                          style={{
                            fontSize: 'var(--font-size-xs)',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: 'var(--radius-full)',
                            background:
                              m.status === 'APPROVED'
                                ? 'rgba(16, 185, 129, 0.15)'
                                : m.status === 'PENDING'
                                ? 'rgba(245, 158, 11, 0.15)'
                                : 'rgba(239, 68, 68, 0.15)',
                            color:
                              m.status === 'APPROVED'
                                ? '#059669'
                                : m.status === 'PENDING'
                                ? '#d97706'
                                : '#dc2626',
                          }}
                        >
                          {m.status}
                        </span>
                      </td>

                      <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                        <span
                          style={{
                            fontSize: 'var(--font-size-xs)',
                            color: m.kyc_verified ? 'var(--color-success-600)' : 'var(--color-warning-600)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          {m.kyc_verified ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
                          {m.kyc_verified ? 'Verified' : 'Pending'}
                        </span>
                      </td>

                      {canApprove && (
                        <td style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'right' }}>
                          <div style={{ display: 'flex', gap: 'var(--space-2)', justifyContent: 'flex-end' }}>
                            {isPending && (
                              <>
                                <button
                                  onClick={() => handleApprove(m.id, m.full_name)}
                                  disabled={actionLoading === m.id}
                                  className="btn btn-primary"
                                  style={{
                                    fontSize: 'var(--font-size-xs)',
                                    padding: '4px 10px',
                                    background: 'var(--color-success-600)',
                                  }}
                                  title="Approve Member"
                                >
                                  <CheckCircle size={14} /> Approve
                                </button>
                                <button
                                  onClick={() => handleReject(m.id, m.full_name)}
                                  disabled={actionLoading === m.id}
                                  className="btn btn-secondary"
                                  style={{
                                    fontSize: 'var(--font-size-xs)',
                                    padding: '4px 10px',
                                    color: 'var(--color-error-500)',
                                  }}
                                  title="Reject Member"
                                >
                                  <XCircle size={14} /> Reject
                                </button>
                              </>
                            )}
                            {isApproved && (
                              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                                Active
                              </span>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination bar */}
        {totalPages > 1 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 'var(--space-4)',
              borderTop: '1px solid var(--border-default)',
            }}
          >
            <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
              Page {page} of {totalPages}
            </span>
            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1 || loading}
                className="btn btn-secondary"
                style={{ fontSize: 'var(--font-size-xs)', padding: '4px 12px' }}
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages || loading}
                className="btn btn-secondary"
                style={{ fontSize: 'var(--font-size-xs)', padding: '4px 12px' }}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
