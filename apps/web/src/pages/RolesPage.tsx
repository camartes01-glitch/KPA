/**
 * Role Management Page — RBAC management for State, District, and Taluka administrators.
 */
import { UserCheck, Plus } from 'lucide-react'

export default function RolesPage() {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Role Management & Scopes</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Assign roles and geographic jurisdictions (State, District, Taluka) to administrators.
          </p>
        </div>
        <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Plus size={16} /> Assign Role
        </button>
      </div>

      <div className="card">
        <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <UserCheck size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-gold-500)', opacity: 0.6 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            Geographic RBAC Scoping
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            Strict role boundaries for State Heads, District Admins, Taluka Admins, and Auditors (Phase 2).
          </p>
        </div>
      </div>
    </div>
  )
}
