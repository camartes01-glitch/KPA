/**
 * Reports Page — Financial reports, membership growth, welfare settlements, and data exports.
 */
import { Download, FileSpreadsheet, FileText } from 'lucide-react'

export default function ReportsPage() {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Reports & Analytics</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Generate analytical statements, membership audit reports, and financial breakdowns.
          </p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-6)',
      }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <FileSpreadsheet size={24} style={{ color: 'var(--color-success-500)' }} />
            <h4 style={{ margin: 0, fontWeight: 600 }}>Membership Master Roll</h4>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0, flex: 1 }}>
            Complete listing of all registered members, approval status, talukas, and contact details.
          </p>
          <button className="btn btn-secondary" style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Download size={14} /> Export CSV
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <FileSpreadsheet size={24} style={{ color: 'var(--color-gold-500)' }} />
            <h4 style={{ margin: 0, fontWeight: 600 }}>Welfare Contributions Ledger</h4>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0, flex: 1 }}>
            Event-wise member contribution debits, payment reconciliation, and disbursement receipts.
          </p>
          <button className="btn btn-secondary" style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Download size={14} /> Export Excel
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <FileText size={24} style={{ color: 'var(--color-primary-500)' }} />
            <h4 style={{ margin: 0, fontWeight: 600 }}>Financial Audit Trail</h4>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0, flex: 1 }}>
            Comprehensive audit report for compliance, chartered accountants, and state executive committee.
          </p>
          <button className="btn btn-secondary" style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Download size={14} /> Export PDF
          </button>
        </div>
      </div>
    </div>
  )
}
