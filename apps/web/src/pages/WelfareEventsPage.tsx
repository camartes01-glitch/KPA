/**
 * Welfare Events Page — Event management and contribution tracking.
 */
import { Heart, Plus, AlertCircle } from 'lucide-react'

export default function WelfareEventsPage() {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Welfare Events</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Create and oversee welfare cases, emergency relief, and member contribution batches.
          </p>
        </div>
        <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Plus size={16} /> Create Welfare Event
        </button>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-6)', background: 'var(--color-primary-50)', border: '1px solid var(--color-primary-200)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          <AlertCircle size={20} style={{ color: 'var(--color-primary-600)', flexShrink: 0 }} />
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-primary-800)', margin: 0 }}>
            Welfare event creation triggers automated idempotent contribution ledger entries across eligible members as configured in Phase 5.
          </p>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Heart size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-error-500)', opacity: 0.6 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            No Active Welfare Events
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            Active cases with target funding, collected amounts, and nominee distribution details will be managed here.
          </p>
        </div>
      </div>
    </div>
  )
}
