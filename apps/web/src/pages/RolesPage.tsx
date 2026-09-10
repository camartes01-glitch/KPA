/**
 * Roles Page — Geographic RBAC Jurisdictions and System Administrator Management.
 */
import { useEffect, useState } from 'react'
import {
  Shield,
  MapPin,
  RefreshCw,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface AdminUser {
  id: string
  phone: string
  name: string | null
  email: string | null
  role: string
  status: string
  is_active: boolean
  district_id: string | null
  taluka_id: string | null
}

interface DistrictItem {
  id: string
  code: string
  name_en: string
  name_kn: string
}

export default function RolesPage() {
  const { user } = useAuthStore()
  const [admins, setAdmins] = useState<AdminUser[]>([])
  const [districts, setDistricts] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      // Load districts for jurisdiction mapping
      const geoRes = await api.get('/geo/districts')
      const distList: DistrictItem[] = geoRes.data.data || []
      const distMap: Record<string, string> = {}
      distList.forEach((d) => {
        distMap[d.id] = `${d.name_en} (${d.code})`
      })
      setDistricts(distMap)

      // Load admins
      const adminRes = await api.get('/auth/admins')
      setAdmins(adminRes.data.data || [])
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to load administrator directory')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

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
            Role Management & RBAC
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Geographic jurisdiction scopes and administrative permissions across Karnataka.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="btn btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Role Scoping Notice */}
      <div
        className="card"
        style={{
          marginBottom: 'var(--space-6)',
          background: 'var(--color-primary-50)',
          border: '1px solid var(--color-primary-200)',
        }}
      >
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          <Shield size={22} color="var(--color-primary-600)" style={{ flexShrink: 0 }} />
          <div>
            <strong style={{ color: 'var(--color-primary-800)', fontSize: 'var(--font-size-sm)' }}>
              Your Active Administrative Scope: {user?.role?.replace('_', ' ')}
            </strong>
            <p style={{ margin: 0, fontSize: 'var(--font-size-xs)', color: 'var(--color-primary-700)' }}>
              {user?.role === 'STATE_HEAD'
                ? 'Full Karnataka Statewide authority — all 31 districts, financial settlements, welfare declarations, and audit logs.'
                : user?.role === 'DISTRICT_ADMIN'
                ? 'District-level jurisdiction — member approvals, KYC reviews, and district broadcast notices.'
                : user?.role === 'TALUKA_ADMIN'
                ? 'Taluka-level jurisdiction — local member queries and taluka notifications.'
                : 'Auditor jurisdiction — read-only immutable access to financial records and system audit trails.'}
            </p>
          </div>
        </div>
      </div>

      {/* Administrators List */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div
          style={{
            padding: 'var(--space-4) var(--space-6)',
            borderBottom: '1px solid var(--border-default)',
            background: 'var(--bg-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, margin: 0 }}>
            Registered Administrators ({admins.length})
          </h3>
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Strict RBAC Jurisdiction Enforcement
          </span>
        </div>

        {loading ? (
          <div style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
            <p>Loading administrators...</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-default)' }}>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Administrator</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Role</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Geographic Jurisdiction</th>
                  <th style={{ padding: 'var(--space-3) var(--space-4)' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {admins.map((adm) => (
                  <tr key={adm.id} style={{ borderBottom: '1px solid var(--border-default)' }}>
                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                        {adm.name || 'Admin User'}
                      </div>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                        {[adm.phone, adm.email || 'No email registered'].filter(Boolean).join(' • ')}
                      </div>
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <span
                        style={{
                          fontSize: 'var(--font-size-xs)',
                          fontWeight: 700,
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-full)',
                          background:
                            adm.role === 'STATE_HEAD'
                              ? 'rgba(37, 99, 235, 0.12)'
                              : adm.role === 'DISTRICT_ADMIN'
                              ? 'rgba(16, 185, 129, 0.12)'
                              : 'rgba(245, 158, 11, 0.12)',
                          color:
                            adm.role === 'STATE_HEAD'
                              ? 'var(--color-primary-700)'
                              : adm.role === 'DISTRICT_ADMIN'
                              ? '#059669'
                              : '#d97706',
                        }}
                      >
                        {adm.role.replace('_', ' ')}
                      </span>
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--font-size-sm)' }}>
                        <MapPin size={14} color="var(--text-muted)" />
                        <span>
                          {adm.district_id
                            ? districts[adm.district_id] || 'Assigned District'
                            : 'All Karnataka (Statewide)'}
                        </span>
                      </div>
                    </td>

                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                      <span
                        style={{
                          fontSize: 'var(--font-size-xs)',
                          fontWeight: 600,
                          color: adm.is_active ? 'var(--color-success-600)' : 'var(--color-error-500)',
                        }}
                      >
                        {adm.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
