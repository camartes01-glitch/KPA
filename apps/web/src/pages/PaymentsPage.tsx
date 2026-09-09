/**
 * Payments Page — Gateway transactions, reconciliations, AutoPay mandates, and receipts.
 */
import { CreditCard, Download } from 'lucide-react'

export default function PaymentsPage() {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Payments & Reconciliation</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Monitor gateway transactions, AutoPay mandates, webhook processing, and settlement reports.
          </p>
        </div>
        <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Download size={16} /> Export Reconciliation CSV
        </button>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-6)',
      }}>
        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Today's Total</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginTop: 4 }}>₹0.00</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Successful</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginTop: 4, color: 'var(--color-success-500)' }}>0</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Pending / Processing</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginTop: 4, color: 'var(--color-warning-500)' }}>0</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>Failed</div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginTop: 4, color: 'var(--color-error-500)' }}>0</div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <CreditCard size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-gold-400)', opacity: 0.6 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            Payment Engine Ready
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            Real-time transaction logs and receipt downloads via Razorpay/Cashfree webhooks wired in Phase 6 & 7.
          </p>
        </div>
      </div>
    </div>
  )
}
