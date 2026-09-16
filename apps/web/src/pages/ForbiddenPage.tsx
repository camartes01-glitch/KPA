import { ShieldAlert } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ForbiddenPage() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '60vh',
      textAlign: 'center',
      padding: 'var(--space-8)',
    }}>
      <div style={{
        width: 80,
        height: 80,
        borderRadius: '50%',
        background: 'rgba(239, 68, 68, 0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 'var(--space-4)',
      }}>
        <ShieldAlert size={44} style={{ color: 'var(--color-danger-500)' }} />
      </div>

      <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginBottom: 'var(--space-2)' }}>
        403 — Access Restricted
      </h1>

      <p style={{ color: 'var(--text-secondary)', maxWidth: 460, lineHeight: 1.6, marginBottom: 'var(--space-6)' }}>
        You do not have administrative permissions to view this resource. Access is strictly enforced according to your assigned KPA role and geographic jurisdiction.
      </p>

      <Link
        to="/dashboard"
        className="btn btn-primary"
        style={{ textDecoration: 'none' }}
      >
        Return to Dashboard
      </Link>
    </div>
  )
}
