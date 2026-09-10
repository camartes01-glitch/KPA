/**
 * Notifications Page — User Announcements, Bilingual Kannada/English alerts, and scoped broadcasts.
 */
import { useEffect, useState } from 'react'
import {
  Bell,
  Send,
  RefreshCw,
  Check,
  Clock,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface NotificationItem {
  id: string
  title: string
  body: string
  channel: string
  type: string
  is_read: boolean
  sent_at: string | null
  created_at: string
}

export default function NotificationsPage() {
  const { user } = useAuthStore()
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [lang, setLang] = useState<'en' | 'kn'>('en')
  const [loading, setLoading] = useState(true)
  const [showBroadcastModal, setShowBroadcastModal] = useState(false)
  const [broadcastLoading, setBroadcastLoading] = useState(false)

  // Broadcast form state
  const [broadcastForm, setBroadcastForm] = useState({
    title_en: '',
    title_kn: '',
    body_en: '',
    body_kn: '',
  })

  const canBroadcast =
    user?.role === 'STATE_HEAD' || user?.role === 'DISTRICT_ADMIN' || user?.role === 'TALUKA_ADMIN'

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const res = await api.get('/notifications/my', { params: { lang } })
      setNotifications(res.data.data || [])
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
  }, [lang])

  const handleMarkAsRead = async (id: string) => {
    try {
      await api.post(`/notifications/${id}/read`)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
    } catch {
      toast.error('Failed to update notification status')
    }
  }

  const handleSendBroadcast = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!broadcastForm.title_en || !broadcastForm.body_en) {
      toast.error('English title and body are required')
      return
    }

    setBroadcastLoading(true)
    try {
      await api.post('/notifications/broadcast', {
        title_en: broadcastForm.title_en,
        title_kn: broadcastForm.title_kn || broadcastForm.title_en,
        body_en: broadcastForm.body_en,
        body_kn: broadcastForm.body_kn || broadcastForm.body_en,
        channel: 'IN_APP',
        type: 'GENERAL_BROADCAST',
      })
      toast.success('Broadcast announcement dispatched successfully')
      setShowBroadcastModal(false)
      setBroadcastForm({ title_en: '', title_kn: '', body_en: '', body_kn: '' })
      fetchNotifications()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to dispatch broadcast')
    } finally {
      setBroadcastLoading(false)
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
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>
            Broadcast & Notifications
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Bilingual Kannada/English alerts, welfare notices, and administrative announcements.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          {/* Language Switcher */}
          <div
            style={{
              display: 'flex',
              background: 'var(--bg-subtle)',
              padding: 3,
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-default)',
            }}
          >
            <button
              onClick={() => setLang('en')}
              className="btn"
              style={{
                fontSize: 'var(--font-size-xs)',
                padding: '4px 10px',
                background: lang === 'en' ? 'var(--color-primary-700)' : 'transparent',
                color: lang === 'en' ? 'white' : 'var(--text-secondary)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              English
            </button>
            <button
              onClick={() => setLang('kn')}
              className="btn"
              style={{
                fontSize: 'var(--font-size-xs)',
                padding: '4px 10px',
                background: lang === 'kn' ? 'var(--color-primary-700)' : 'transparent',
                color: lang === 'kn' ? 'white' : 'var(--text-secondary)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              ಕನ್ನಡ (Kannada)
            </button>
          </div>

          <button
            onClick={fetchNotifications}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>

          {canBroadcast && (
            <button
              onClick={() => setShowBroadcastModal(true)}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
            >
              <Send size={16} /> New Broadcast
            </button>
          )}
        </div>
      </div>

      {/* Notifications Feed */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
            <p>Loading notification feed...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div style={{ padding: 'var(--space-12) var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Bell size={48} style={{ margin: '0 auto var(--space-4)', color: 'var(--color-primary-500)', opacity: 0.4 }} />
            <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
              No Notifications
            </h3>
            <p style={{ maxWidth: 460, margin: '0 auto', fontSize: 'var(--font-size-sm)' }}>
              You have no notifications in your inbox at this time.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {notifications.map((n) => (
              <div
                key={n.id}
                style={{
                  padding: 'var(--space-4) var(--space-6)',
                  borderBottom: '1px solid var(--border-default)',
                  background: n.is_read ? 'transparent' : 'rgba(37, 99, 235, 0.03)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: 'var(--space-4)',
                }}
              >
                <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'flex-start', flex: 1 }}>
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 'var(--radius-full)',
                      background: n.is_read ? 'var(--bg-subtle)' : 'var(--color-primary-100)',
                      color: n.is_read ? 'var(--text-muted)' : 'var(--color-primary-700)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <Bell size={18} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 2 }}>
                      <h4 style={{ margin: 0, fontWeight: 700, fontSize: 'var(--font-size-base)', color: 'var(--text-primary)' }}>
                        {n.title}
                      </h4>
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '1px 6px',
                          borderRadius: 'var(--radius-full)',
                          background: 'var(--bg-subtle)',
                          color: 'var(--text-muted)',
                        }}
                      >
                        {n.type}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', margin: '4px 0 6px 0' }}>
                      {n.body}
                    </p>
                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Clock size={12} />
                      {new Date(n.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>

                {!n.is_read && (
                  <button
                    onClick={() => handleMarkAsRead(n.id)}
                    className="btn btn-secondary"
                    style={{ fontSize: 'var(--font-size-xs)', padding: '4px 8px', flexShrink: 0 }}
                    title="Mark as read"
                  >
                    <Check size={14} /> Mark Read
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Broadcast Modal */}
      {showBroadcastModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)',
          }}
        >
          <div
            className="card"
            style={{ width: '100%', maxWidth: 540, boxShadow: 'var(--shadow-xl)' }}
          >
            <h3 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800, marginBottom: 'var(--space-2)' }}>
              Dispatch Scoped Broadcast
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', marginBottom: 'var(--space-4)' }}>
              This announcement will be delivered to all photographers within your jurisdiction (
              {user?.role?.replace('_', ' ')}).
            </p>

            <form onSubmit={handleSendBroadcast} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div>
                <label className="form-label">English Title *</label>
                <input
                  type="text"
                  className="input"
                  required
                  placeholder="e.g. Annual District Photography Exhibition"
                  value={broadcastForm.title_en}
                  onChange={(e) => setBroadcastForm({ ...broadcastForm, title_en: e.target.value })}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label className="form-label">Kannada Title (Optional)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. ವಾರ್ಷಿಕ ಜಿಲ್ಲಾ ಛಾಯಾಗ್ರಹಣ ಪ್ರದರ್ಶನ"
                  value={broadcastForm.title_kn}
                  onChange={(e) => setBroadcastForm({ ...broadcastForm, title_kn: e.target.value })}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label className="form-label">English Announcement Body *</label>
                <textarea
                  className="input"
                  required
                  rows={3}
                  placeholder="Enter details of the announcement..."
                  value={broadcastForm.body_en}
                  onChange={(e) => setBroadcastForm({ ...broadcastForm, body_en: e.target.value })}
                  style={{ width: '100%', resize: 'vertical' }}
                />
              </div>

              <div>
                <label className="form-label">Kannada Announcement Body (Optional)</label>
                <textarea
                  className="input"
                  rows={3}
                  placeholder="ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ..."
                  value={broadcastForm.body_kn}
                  onChange={(e) => setBroadcastForm({ ...broadcastForm, body_kn: e.target.value })}
                  style={{ width: '100%', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-4)' }}>
                <button
                  type="button"
                  onClick={() => setShowBroadcastModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={broadcastLoading}
                  className="btn btn-primary"
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
                >
                  <Send size={16} />
                  {broadcastLoading ? 'Dispatching...' : 'Dispatch Broadcast'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
