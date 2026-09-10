/**
 * Audit Logs Page — Immutable compliance trail for administrative and security actions.
 */
import { useEffect, useState, useCallback } from 'react'
import {
  Shield,
  Search,
  RefreshCw,
  Lock,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface AuditLogItem {
  id: string
  user_id: string | null
  action: string
  resource_type: string
  resource_id: string | null
  payload_json: string | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

export default function AuditLogsPage() {
  const { user } = useAuthStore()
  const [logs, setLogs] = useState<AuditLogItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [actionFilter, setActionFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const isAuthorized = user?.role === 'STATE_HEAD' || user?.role === 'AUDITOR'

  const fetchLogs = useCallback(async () => {
    if (!isAuthorized) {
      setLoading(false)
      return
    }

    setLoading(true)
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
      }
      if (actionFilter.trim()) params.action = actionFilter.trim()

      const response = await api.get('/audit-logs', { params })
      const data = response.data
      setLogs(data.data || [])
      setTotal(data.total || 0)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to load system audit trail')
    } finally {
      setLoading(false)
    }
  }, [isAuthorized, page, pageSize, actionFilter])

  useEffect(() => {
    fetchLogs()
  }, [fetchLogs])

  if (!isAuthorized) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
        <Lock size={48} color="var(--color-error-500)" style={{ margin: '0 auto var(--space-4)', opacity: 0.8 }} />
        <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 8 }}>
          Access Restricted by RBAC
        </h2>
        <p style={{ color: 'var(--text-secondary)', maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
          System Audit Logs contain tamper-evident logs of administrative actions and are strictly limited
          to <strong>State Head</strong> and <strong>Auditor</strong> roles.
        </p>
      </div>
    )
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
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>System Audit Logs</h1>
            <span
              style={{
                background: 'rgba(37, 99, 235, 0.12)',
                color: 'var(--color-primary-700)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <Shield size={12} />
              Immutable Ledger
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Tamper-evident logs of administrative approvals, welfare events, settlements, and security events.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="btn btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Filter */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: 12,
                top: '50%',
                transform: 'translateY(-50)',
                color: 'var(--text-muted)',
              }}
            />
            <input
              type="text"
              placeholder="Filter by action keyword (e.g. AUTH, APPROVE, WELFARE)..."
              className="input"
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value)
                setPage(1)
              }}
              style={{ paddingLeft: 40, width: '100%' }}
            />
          </div>
          <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
            Total: <strong>{total}</strong> entries
          </span>
        </div>
      </div>

      {/* Logs Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
            <p>Loading audit trail...</p>
          </div>
        ) : logs.length === 0 ? (
          <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Shield size={48} style={{ margin: '0 auto var(--space-4)', opacity: 0.4 }} />
            <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>No Audit Entries</h3>
            <p style={{ fontSize: 'var(--font-size-sm)' }}>
              {actionFilter ? 'No audit entries match the current filter.' : 'Audit logs are generated as administrative actions occur.'}
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border-default)', textAlign: 'left' }}>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Timestamp</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Action</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Resource Type</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Resource ID</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Origin IP / Client</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: '1px solid var(--border-default)' }}>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', whiteSpace: 'nowrap' }}>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-primary)', fontWeight: 600 }}>
                        {new Date(log.created_at).toLocaleDateString()}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {new Date(log.created_at).toLocaleTimeString()}
                      </div>
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <span
                        style={{
                          fontFamily: 'monospace',
                          fontSize: 'var(--font-size-xs)',
                          fontWeight: 700,
                          background: 'rgba(37, 99, 235, 0.08)',
                          color: 'var(--color-primary-700)',
                          padding: '2px 6px',
                          borderRadius: 'var(--radius-sm)',
                        }}
                      >
                        {log.action}
                      </span>
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-sm)' }}>
                      {log.resource_type}
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <span
                        style={{
                          fontFamily: 'monospace',
                          fontSize: 11,
                          color: 'var(--text-muted)',
                        }}
                      >
                        {log.resource_id ? `${log.resource_id.slice(0, 8)}...` : '—'}
                      </span>
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                      <div>{log.ip_address || '127.0.0.1'}</div>
                      <div style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {log.user_agent || 'Client'}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
