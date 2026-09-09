/**
 * Notifications Page — Broadcast messages, SMS, FCM push notifications.
 */
import { Bell, Send } from 'lucide-react'

export default function NotificationsPage() {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800 }}>Broadcast & Notifications</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Send push notifications (FCM), SMS alerts, and announcements to members by district/taluka scope.
          </p>
        </div>
        <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Send size={16} /> New Broadcast
        </button>
      </div>

      <div className="card">
        <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Bell size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-primary-500)', opacity: 0.6 }} />
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            Notification Dispatch System
          </h3>
          <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
            Configured with bilingual English & Kannada templates and Celery/Redis queue background delivery (Phase 8).
          </p>
        </div>
      </div>
    </div>
  )
}
