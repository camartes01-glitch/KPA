/**
 * Receipts Page — List, Search, Filter, View, Print & Download Official KPA Welfare Receipts.
 */
import { useState, useEffect } from 'react'
import {
  Search,
  Printer,
  Download,
  CheckCircle2,
  Clock,
  XCircle,
  RefreshCw,
  Eye,
} from 'lucide-react'
import { api, extractErrorMessage } from '@/lib/api'

interface Receipt {
  id: string
  receipt_no: string
  amount: number
  currency: string
  status: 'CAPTURED' | 'CREATED' | 'AUTHORIZED' | 'FAILED' | 'REFUNDED'
  payment_method: string | null
  gateway_order_id: string
  gateway_payment_id: string | null
  member_name: string
  membership_no: string | null
  event_title: string | null
  paid_at: string | null
  created_at: string
}

export default function ReceiptsPage() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(15)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null)

  const fetchReceipts = async () => {
    setLoading(true)
    setError(null)
    try {
      const params: any = { page, page_size: pageSize }
      if (search.trim()) params.search = search.trim()
      if (statusFilter) params.status = statusFilter

      const res = await api.get('/payments/receipts', { params })
      if (res.data?.success) {
        setReceipts(res.data.data)
        setTotal(res.data.total)
        setTotalPages(res.data.total_pages)
      }
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReceipts()
  }, [page, statusFilter])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchReceipts()
  }

  const handlePrint = () => {
    window.print()
  }

  const handleDownloadText = (r: Receipt) => {
    const text = `
============================================================
       KARNATAKA PHOTOGRAPHY ASSOCIATION (REGD.)
             OFFICIAL WELFARE MUTUAL DEBIT RECEIPT
============================================================
Receipt No:      ${r.receipt_no}
Date & Time:     ${new Date(r.paid_at || r.created_at).toLocaleString('en-IN')}
Member Name:     ${r.member_name}
Membership No:   ${r.membership_no || 'N/A'}
Welfare Relief:  ${r.event_title || 'General Welfare Fund'}
Amount Settled:  ₹${r.amount.toFixed(2)} (${r.currency})
Payment Mode:    ${r.payment_method || 'UPI / AutoPay'}
Gateway Order:   ${r.gateway_order_id}
Transaction ID:  ${r.gateway_payment_id || 'N/A'}
Status:          ${r.status}
============================================================
Certified by Karnataka Photography Association State Committee
Valid across all 31 Districts of Karnataka.
============================================================
`
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${r.receipt_no}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getStatusBadge = (status: Receipt['status']) => {
    switch (status) {
      case 'CAPTURED':
        return (
          <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <CheckCircle2 size={13} /> Verified
          </span>
        )
      case 'CREATED':
      case 'AUTHORIZED':
        return (
          <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <Clock size={13} /> Pending
          </span>
        )
      default:
        return (
          <span className="badge badge-danger" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <XCircle size={13} /> Failed
          </span>
        )
    }
  }

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Welfare Receipts</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Official verified payment vouchers and member debit records ({total} total)
          </p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={fetchReceipts}
          disabled={loading}
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Filters Bar */}
      <div className="card" style={{ marginBottom: 'var(--space-6)', padding: 'var(--space-4)' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 260, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="form-control"
              placeholder="Search by receipt no, member name, or membership ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: 38 }}
            />
          </div>

          <div style={{ width: 180 }}>
            <select
              className="form-control"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All Statuses</option>
              <option value="CAPTURED">Verified (Captured)</option>
              <option value="CREATED">Pending</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary">
            Filter
          </button>
        </form>
      </div>

      {/* Error state */}
      {error && (
        <div className="card" style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: 'var(--color-danger-500)', marginBottom: 'var(--space-6)' }}>
          <p style={{ color: 'var(--color-danger-500)', margin: 0 }}>{error}</p>
        </div>
      )}

      {/* Table Card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'var(--bg-card-header)' }}>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'left', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Receipt No</th>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'left', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Member</th>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'left', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Event / Case</th>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'right', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Amount</th>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'center', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Status</th>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'left', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Date & Time</th>
                <th style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'center', fontSize: 'var(--font-size-xs)', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && receipts.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-secondary)' }}>
                    Loading official receipts...
                  </td>
                </tr>
              ) : receipts.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-secondary)' }}>
                    No receipts found matching the selected criteria.
                  </td>
                </tr>
              ) : (
                receipts.map((r) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontWeight: 600, color: 'var(--color-gold-400)', fontFamily: 'monospace' }}>
                      {r.receipt_no}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <div style={{ fontWeight: 600 }}>{r.member_name}</div>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                        {r.membership_no || 'Pending ID'}
                      </div>
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                      {r.event_title || 'Mutual Welfare Fund'}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'right', fontWeight: 700 }}>
                      ₹{r.amount.toFixed(2)}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'center' }}>
                      {getStatusBadge(r.status)}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                      {new Date(r.paid_at || r.created_at).toLocaleString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td style={{ padding: 'var(--space-3) var(--space-4)', textAlign: 'center' }}>
                      <button
                        className="btn btn-secondary"
                        onClick={() => setSelectedReceipt(r)}
                        style={{ padding: '4px 10px', fontSize: 'var(--font-size-xs)', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                      >
                        <Eye size={13} /> View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--space-4)', borderTop: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
              Page {page} of {totalPages}
            </span>
            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
              <button
                className="btn btn-secondary"
                disabled={page <= 1 || loading}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <button
                className="btn btn-secondary"
                disabled={page >= totalPages || loading}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal Dialog for View Receipt */}
      {selectedReceipt && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: 'var(--space-4)',
        }}>
          <div className="card" style={{ maxWidth: 580, width: '100%', background: 'var(--bg-card)', padding: 'var(--space-6)', border: '2px solid var(--color-gold-500)' }}>
            {/* Modal Header */}
            <div style={{ textAlign: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
              <div style={{ color: 'var(--color-gold-400)', fontWeight: 800, fontSize: 'var(--font-size-lg)', letterSpacing: 0.5 }}>
                KARNATAKA PHOTOGRAPHY ASSOCIATION (REGD.)
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', margin: '2px 0 6px 0' }}>
                ಕರ್ನಾಟಕ ಛಾಯಾಗ್ರಾಹಕರ ಸಂಘ (ರಿ.) • State Committee
              </div>
              <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
                OFFICIAL MUTUAL RELIEF DEBIT RECEIPT
              </div>
            </div>

            {/* Receipt Details */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', fontSize: 'var(--font-size-sm)', marginBottom: 'var(--space-6)' }}>
              <div>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>RECEIPT NO</span>
                <strong style={{ color: 'var(--color-gold-400)', fontFamily: 'monospace' }}>{selectedReceipt.receipt_no}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>DATE & TIME</span>
                <strong>{new Date(selectedReceipt.paid_at || selectedReceipt.created_at).toLocaleString('en-IN')}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>MEMBER NAME</span>
                <strong>{selectedReceipt.member_name}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>MEMBERSHIP ID</span>
                <strong>{selectedReceipt.membership_no || 'N/A'}</strong>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>WELFARE RELIEF CASE</span>
                <strong>{selectedReceipt.event_title || 'State Welfare Mutual Fund'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>GATEWAY ORDER</span>
                <span style={{ fontFamily: 'monospace', fontSize: 'var(--font-size-xs)' }}>{selectedReceipt.gateway_order_id}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', display: 'block' }}>PAYMENT REFERENCE</span>
                <span style={{ fontFamily: 'monospace', fontSize: 'var(--font-size-xs)' }}>{selectedReceipt.gateway_payment_id || 'N/A'}</span>
              </div>
            </div>

            {/* Total Section */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 'var(--space-4)',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: 'var(--radius-md)',
              marginBottom: 'var(--space-6)',
            }}>
              <div>
                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>Amount Paid</span>
                <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, color: 'var(--color-success-500)' }}>
                  ₹{selectedReceipt.amount.toFixed(2)}
                </div>
              </div>
              <div>
                {getStatusBadge(selectedReceipt.status)}
              </div>
            </div>

            {/* Modal Actions */}
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
              <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                <button className="btn btn-secondary" onClick={handlePrint} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Printer size={15} /> Print
                </button>
                <button className="btn btn-secondary" onClick={() => handleDownloadText(selectedReceipt)} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Download size={15} /> Download
                </button>
              </div>

              <button className="btn btn-primary" onClick={() => setSelectedReceipt(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
