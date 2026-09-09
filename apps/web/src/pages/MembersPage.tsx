/**
 * Members Page — Directory, search, filter, and verification management.
 */
import { Users, Search, Plus, Filter, Download } from 'lucide-react'

export default function MembersPage() {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Member Directory</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Manage KPA registered photographers, registrations, and verification workflows.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Download size={16} /> Export
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Plus size={16} /> Add Member
          </button>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 260, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search by name, membership number, phone..."
              className="input"
              style={{ paddingLeft: 40 }}
            />
          </div>
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Filter size={16} /> Filter
          </button>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Users size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-primary-400)', opacity: 0.6 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            Member Management Module
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            Connected to Phase 4 Member Workflow & APIs. Member registration, ID card generation, and KYC approvals will appear here.
          </p>
        </div>
      </div>
    </div>
  )
}
