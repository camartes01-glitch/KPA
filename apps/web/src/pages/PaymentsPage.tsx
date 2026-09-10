/**
 * Payments Page — Gateway transactions, collection metrics, and official receipt lookup.
 */
import { useEffect, useState } from 'react'
import {
  Download,
  Search,
  Receipt,
  ShieldCheck,
} from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface ReceiptData {
  id: string
  receipt_no: string
  amount: number
  currency: string
  status: string
  payment_method: string | null
  gateway_order_id: string
  gateway_payment_id: string | null
  member_name: string
  membership_no: string | null
  event_title: string | null
  paid_at: string | null
  created_at: string
}

export default function PaymentsPage() {
  const [metrics, setMetrics] = useState<{
    today: number
    monthly: number
    pending: number
    autopay: number
  }>({ today: 0, monthly: 0, pending: 0, autopay: 0 })
  const [receiptNo, setReceiptNo] = useState('')
  const [receipt, setReceipt] = useState<ReceiptData | null>(null)
  const [loadingReceipt, setLoadingReceipt] = useState(false)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await api.get('/dashboard/metrics')
        const data = res.data.data
        if (data) {
          setMetrics({
            today: data.total_collected_today,
            monthly: data.total_collected_monthly,
            pending: data.total_pending_dues,
            autopay: data.autopay_active_members,
          })
        }
      } catch {
        // Handled silently
      }
    }
    fetchMetrics()
  }, [])

  const handleLookupReceipt = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!receiptNo.trim()) return
    setLoadingReceipt(true)
    setReceipt(null)
    try {
      const res = await api.get(`/payments/receipt/${receiptNo.trim()}`)
      setReceipt(res.data.data)
      toast.success('Official payment receipt found')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Receipt not found. Verify receipt number.')
    } finally {
      setLoadingReceipt(false)
    }
  }

  const handleExportCsv = async () => {
    setExporting(true)
    try {
      const response = await api.get('/reports/financial/csv', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'kpa_financial_audit_statement.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Financial transaction statement downloaded')
    } catch {
      toast.error('Failed to export reconciliation CSV')
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
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>Payments & Reconciliation</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            UPI transaction audits, official payment receipts, and gateway reconciliation logs.
          </p>
        </div>

        <button
          onClick={handleExportCsv}
          disabled={exporting}
          className="btn btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <Download size={16} />
          {exporting ? 'Exporting...' : 'Export Financial Statement'}
        </button>
      </div>

      {/* KPI Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-6)',
        }}
      >
        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Today's Total</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginTop: 4, color: 'var(--color-gold-500)' }}>
            ₹{metrics.today.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
            Settled collections
          </div>
        </div>

        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Monthly Collection</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginTop: 4, color: 'var(--color-primary-700)' }}>
            ₹{metrics.monthly.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
            Current billing cycle
          </div>
        </div>

        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>AutoPay Active</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginTop: 4, color: 'var(--color-success-600)' }}>
            {metrics.autopay}
          </div>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
            E-mandates registered
          </div>
        </div>

        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Pending Dues</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginTop: 4, color: 'var(--color-error-500)' }}>
            ₹{metrics.pending.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
            Unsettled obligations
          </div>
        </div>
      </div>

      {/* Official Receipt Verification Section */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, margin: 0 }}>
            Official Payment Receipt Lookup
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', marginTop: 2 }}>
            Verify cryptographic receipt numbers issued for member welfare contributions.
          </p>
        </div>

        <form onSubmit={handleLookupReceipt} style={{ display: 'flex', gap: 'var(--space-3)', maxWidth: 500 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search
              size={18}
              style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              placeholder="Enter receipt number (e.g. KPA-DEMO-RCP)..."
              className="input"
              value={receiptNo}
              onChange={(e) => setReceiptNo(e.target.value)}
              style={{ paddingLeft: 40, width: '100%' }}
            />
          </div>
          <button type="submit" disabled={loadingReceipt} className="btn btn-primary">
            {loadingReceipt ? 'Searching...' : 'Lookup'}
          </button>
        </form>

        {/* Receipt Display */}
        {receipt && (
          <div
            style={{
              marginTop: 'var(--space-6)',
              padding: 'var(--space-6)',
              background: 'var(--bg-subtle)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--border-default)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)', borderBottom: '1px solid var(--border-default)', paddingBottom: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <Receipt size={24} color="var(--color-primary-600)" />
                <div>
                  <h4 style={{ margin: 0, fontWeight: 700, fontSize: 'var(--font-size-base)' }}>
                    Receipt #{receipt.receipt_no}
                  </h4>
                  <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                    Issued on {new Date(receipt.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
              <span
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#059669',
                  padding: '3px 10px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                <ShieldCheck size={14} />
                {receipt.status}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)', fontSize: 'var(--font-size-sm)' }}>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>Member Name:</span>
                <div style={{ fontWeight: 600 }}>{receipt.member_name}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>Membership ID:</span>
                <div style={{ fontWeight: 600, fontFamily: 'monospace' }}>{receipt.membership_no || 'PENDING'}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>Welfare Event:</span>
                <div style={{ fontWeight: 600 }}>{receipt.event_title || 'Mutual Relief Contribution'}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>Amount Paid:</span>
                <div style={{ fontWeight: 800, fontSize: 'var(--font-size-lg)', color: 'var(--color-primary-700)' }}>
                  ₹{receipt.amount} {receipt.currency}
                </div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>Payment Method:</span>
                <div style={{ fontWeight: 600 }}>{receipt.payment_method || 'UPI'}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>Gateway Order ID:</span>
                <div style={{ fontWeight: 600, fontFamily: 'monospace', fontSize: 'var(--font-size-xs)' }}>
                  {receipt.gateway_order_id}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
