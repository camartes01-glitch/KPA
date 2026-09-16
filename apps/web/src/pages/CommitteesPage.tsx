/**
 * Committees Page — Executive Committee Governance & Office Bearers Administration.
 */
import { useEffect, useState } from 'react'
import {
  Plus,
  RefreshCw,
  Phone,
  Mail,
  Calendar,
  Trash2,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface CommitteeMember {
  id: string
  name: string
  phone: string
  email?: string | null
  designation: string
  committee_level: 'STATE' | 'DISTRICT' | 'TALUKA' | string
  district_id?: string | null
  district_name?: string | null
  taluka_id?: string | null
  taluka_name?: string | null
  tenure_start: string
  tenure_end?: string | null
  is_active: boolean
}

interface DistrictOption {
  id: string
  name_en: string
  code: string
}

export default function CommitteesPage() {
  const { user } = useAuthStore()
  const [roster, setRoster] = useState<CommitteeMember[]>([])
  const [districts, setDistricts] = useState<DistrictOption[]>([])
  const [selectedLevel, setSelectedLevel] = useState<'ALL' | 'STATE' | 'DISTRICT' | 'TALUKA'>('ALL')
  const [selectedDistrict, setSelectedDistrict] = useState<string>('')
  const [loading, setLoading] = useState(true)

  // Modal
  const [showAppointModal, setShowAppointModal] = useState(false)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [designation, setDesignation] = useState('Executive Member')
  const [level, setLevel] = useState('DISTRICT')
  const [districtId, setDistrictId] = useState('')
  const [tenureStart, setTenureStart] = useState('2024-01-01')
  const [tenureEnd, setTenureEnd] = useState('2026-12-31')

  const canManage = user?.role === 'STATE_HEAD' || user?.role === 'DISTRICT_ADMIN'

  const fetchData = async () => {
    setLoading(true)
    try {
      const [comRes, distRes] = await Promise.all([
        api.get('/committees'),
        api.get('/geo/districts'),
      ])
      setRoster(comRes.data.data || [])
      setDistricts(distRes.data.data || [])
    } catch {
      toast.error('Failed to load committee roster')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleAppoint = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/committees', {
        name,
        phone,
        email: email || undefined,
        designation,
        committee_level: level,
        district_id: level !== 'STATE' && districtId ? districtId : undefined,
        tenure_start: tenureStart,
        tenure_end: tenureEnd || undefined,
      })
      toast.success(`${designation} appointed successfully`)
      setShowAppointModal(false)
      setName('')
      setPhone('')
      setEmail('')
      fetchData()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg || 'Failed to appoint office bearer')
    }
  }

  const handleRemove = async (id: string, memberName: string) => {
    if (!window.confirm(`Conclude tenure for ${memberName}?`)) return
    try {
      await api.delete(`/committees/${id}`)
      toast.success(`Removed ${memberName} from committee`)
      fetchData()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg || 'Failed to remove committee member')
    }
  }

  const filteredRoster = roster.filter((m) => {
    if (selectedLevel !== 'ALL' && m.committee_level !== selectedLevel) return false
    if (selectedDistrict && m.district_id !== selectedDistrict) return false
    return true
  })

  return (
    <div>
      {/* Header */}
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
            Committee Administration
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            State Executive Committee, District Bodies, and Taluka Office Bearers.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          {canManage && (
            <button
              onClick={() => setShowAppointModal(true)}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
            >
              <Plus size={16} /> Appoint Office Bearer
            </button>
          )}
          <button
            onClick={fetchData}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--space-3)',
          marginBottom: 'var(--space-6)',
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', background: 'var(--bg-card)', padding: 4, borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-default)' }}>
          {(['ALL', 'STATE', 'DISTRICT', 'TALUKA'] as const).map((lvl) => (
            <button
              key={lvl}
              onClick={() => setSelectedLevel(lvl)}
              style={{
                padding: '6px 14px',
                fontSize: 'var(--font-size-sm)',
                fontWeight: selectedLevel === lvl ? 700 : 500,
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: selectedLevel === lvl ? 'var(--color-primary-600)' : 'transparent',
                color: selectedLevel === lvl ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {lvl === 'ALL' ? 'All Committees' : `${lvl} Committee`}
            </button>
          ))}
        </div>

        {selectedLevel !== 'STATE' && (
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-default)',
              fontSize: 'var(--font-size-sm)',
              background: 'var(--bg-card)',
            }}
          >
            <option value="">All Districts</option>
            {districts.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name_en} ({d.code})
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Roster Cards Grid */}
      {loading ? (
        <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
          <p>Loading committee office bearers...</p>
        </div>
      ) : filteredRoster.length === 0 ? (
        <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center', color: 'var(--text-muted)' }}>
          No committee members found matching the selected filters.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
          {filteredRoster.map((m) => (
            <div key={m.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 800,
                      letterSpacing: 0.5,
                      textTransform: 'uppercase',
                      color: 'var(--color-gold-600)',
                    }}
                  >
                    {m.committee_level} EXECUTIVE
                  </span>
                  <h3 style={{ margin: '2px 0', fontSize: 'var(--font-size-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {m.name}
                  </h3>
                  <span
                    style={{
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 700,
                      color: 'var(--color-primary-700)',
                      background: 'var(--color-primary-50)',
                      padding: '2px 8px',
                      borderRadius: 999,
                      display: 'inline-block',
                      marginTop: 2,
                    }}
                  >
                    {m.designation}
                  </span>
                </div>

                {canManage && (
                  <button
                    onClick={() => handleRemove(m.id, m.name)}
                    style={{
                      border: 'none',
                      background: 'transparent',
                      color: 'var(--color-error-500)',
                      cursor: 'pointer',
                      padding: 4,
                    }}
                    title="Conclude tenure"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>

              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: 4 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Phone size={13} /> {m.phone}
                </div>
                {m.email && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Mail size={13} /> {m.email}
                  </div>
                )}
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Calendar size={13} /> Tenure: {m.tenure_start} to {m.tenure_end || 'Present'}
                </div>
                {m.district_name && (
                  <div style={{ marginTop: 2, fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Jurisdiction: {m.district_name}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Appoint Office Bearer Modal */}
      {showAppointModal && (
        <div className="modal-backdrop">
          <div className="modal" style={{ maxWidth: 480 }}>
            <h3 style={{ margin: '0 0 var(--space-4)' }}>Appoint Committee Office Bearer</h3>
            <form onSubmit={handleAppoint} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div>
                <label className="label">Full Name</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. Sri Ramesh Kumar"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div>
                <label className="label">Mobile Number</label>
                <input
                  required
                  className="input"
                  placeholder="+91 98765 43210"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>

              <div>
                <label className="label">Email Address (Optional)</label>
                <input
                  type="email"
                  className="input"
                  placeholder="leader@kpa.org.in"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <div>
                  <label className="label">Committee Level</label>
                  <select
                    className="input"
                    value={level}
                    onChange={(e) => setLevel(e.target.value)}
                  >
                    {user?.role === 'STATE_HEAD' && <option value="STATE">State Executive</option>}
                    <option value="DISTRICT">District Committee</option>
                    <option value="TALUKA">Taluka Committee</option>
                  </select>
                </div>

                <div>
                  <label className="label">Designation</label>
                  <select
                    className="input"
                    value={designation}
                    onChange={(e) => setDesignation(e.target.value)}
                  >
                    <option value="President">President</option>
                    <option value="Vice President">Vice President</option>
                    <option value="General Secretary">General Secretary</option>
                    <option value="Joint Secretary">Joint Secretary</option>
                    <option value="Treasurer">Treasurer</option>
                    <option value="Executive Member">Executive Member</option>
                  </select>
                </div>
              </div>

              {level !== 'STATE' && (
                <div>
                  <label className="label">Jurisdiction District</label>
                  <select
                    required
                    className="input"
                    value={districtId}
                    onChange={(e) => setDistrictId(e.target.value)}
                  >
                    <option value="">Select District</option>
                    {districts.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name_en} ({d.code})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <div>
                  <label className="label">Tenure Start</label>
                  <input
                    type="date"
                    required
                    className="input"
                    value={tenureStart}
                    onChange={(e) => setTenureStart(e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">Tenure End</label>
                  <input
                    type="date"
                    className="input"
                    value={tenureEnd}
                    onChange={(e) => setTenureEnd(e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
                <button type="button" onClick={() => setShowAppointModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Confirm Appointment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
