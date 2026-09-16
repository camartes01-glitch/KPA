/**
 * Districts & Talukas Management Page — Karnataka 31 Districts Master Data and Hierarchy.
 */
import { useEffect, useState } from 'react'
import {
  Plus,
  RefreshCw,
  Search,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface TalukaItem {
  id: string
  name_en: string
  name_kn: string
  code: string
  is_active: boolean
}

interface DistrictItem {
  id: string
  name_en: string
  name_kn: string
  code: string
  is_active: boolean
  talukas?: TalukaItem[]
}

export default function DistrictsPage() {
  const { user } = useAuthStore()
  const [districts, setDistricts] = useState<DistrictItem[]>([])
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictItem | null>(null)
  const [talukas, setTalukas] = useState<TalukaItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  // Modals
  const [showAddDistrict, setShowAddDistrict] = useState(false)
  const [newDistEn, setNewDistEn] = useState('')
  const [newDistKn, setNewDistKn] = useState('')
  const [newDistCode, setNewDistCode] = useState('')

  const [showAddTaluka, setShowAddTaluka] = useState(false)
  const [newTalEn, setNewTalEn] = useState('')
  const [newTalKn, setNewTalKn] = useState('')
  const [newTalCode, setNewTalCode] = useState('')

  const isStateHead = user?.role === 'STATE_HEAD'

  const fetchDistricts = async () => {
    setLoading(true)
    try {
      const res = await api.get('/geo/districts')
      const data: DistrictItem[] = res.data.data || []
      setDistricts(data)
      if (data.length > 0 && !selectedDistrict) {
        selectDistrict(data[0])
      }
    } catch {
      toast.error('Failed to load districts')
    } finally {
      setLoading(false)
    }
  }

  const selectDistrict = async (d: DistrictItem) => {
    setSelectedDistrict(d)
    try {
      const res = await api.get(`/geo/districts/${d.id}/talukas`)
      setTalukas(res.data.data || [])
    } catch {
      toast.error(`Failed to load talukas for ${d.name_en}`)
    }
  }

  useEffect(() => {
    fetchDistricts()
  }, [])

  const handleCreateDistrict = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/geo/districts', {
        name_en: newDistEn,
        name_kn: newDistKn,
        code: newDistCode.toUpperCase(),
      })
      toast.success(`District ${newDistEn} created successfully`)
      setShowAddDistrict(false)
      setNewDistEn('')
      setNewDistKn('')
      setNewDistCode('')
      fetchDistricts()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg || 'Failed to create district')
    }
  }

  const handleCreateTaluka = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedDistrict) return
    try {
      await api.post('/geo/talukas', {
        district_id: selectedDistrict.id,
        name_en: newTalEn,
        name_kn: newTalKn,
        code: newTalCode.toUpperCase(),
      })
      toast.success(`Taluka ${newTalEn} created successfully`)
      setShowAddTaluka(false)
      setNewTalEn('')
      setNewTalKn('')
      setNewTalCode('')
      selectDistrict(selectedDistrict)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg || 'Failed to create taluka')
    }
  }

  const toggleDistrictStatus = async (d: DistrictItem) => {
    if (!isStateHead) return
    try {
      await api.patch(`/geo/districts/${d.id}`, { is_active: !d.is_active })
      toast.success(`District ${d.name_en} ${!d.is_active ? 'activated' : 'deactivated'}`)
      fetchDistricts()
    } catch {
      toast.error('Failed to update district status')
    }
  }

  const toggleTalukaStatus = async (t: TalukaItem) => {
    if (!isStateHead || !selectedDistrict) return
    try {
      await api.patch(`/geo/talukas/${t.id}`, { is_active: !t.is_active })
      toast.success(`Taluka ${t.name_en} ${!t.is_active ? 'activated' : 'deactivated'}`)
      selectDistrict(selectedDistrict)
    } catch {
      toast.error('Failed to update taluka status')
    }
  }

  const filteredDistricts = districts.filter(
    (d) =>
      d.name_en.toLowerCase().includes(search.toLowerCase()) ||
      d.name_kn.includes(search) ||
      d.code.toLowerCase().includes(search.toLowerCase())
  )

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
            Districts & Talukas
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Geographic jurisdiction hierarchy across all 31 Karnataka administrative districts.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          {isStateHead && (
            <button
              onClick={() => setShowAddDistrict(true)}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
            >
              <Plus size={16} />
              Add District
            </button>
          )}
          <button
            onClick={fetchDistricts}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Grid Layout: Districts Left, Talukas Right */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(360px, 1.4fr)', gap: 'var(--space-6)' }}>
        {/* District Selection Column */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--border-default)' }}>
            <div style={{ position: 'relative' }}>
              <Search
                size={16}
                style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-muted)' }}
              />
              <input
                type="text"
                placeholder="Search districts (English / ಕನ್ನಡ)..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px 8px 36px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-default)',
                  fontSize: 'var(--font-size-sm)',
                }}
              />
            </div>
          </div>

          <div style={{ maxHeight: 600, overflowY: 'auto' }}>
            {loading ? (
              <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
                Loading districts...
              </div>
            ) : filteredDistricts.length === 0 ? (
              <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
                No districts found
              </div>
            ) : (
              filteredDistricts.map((d) => {
                const isSelected = selectedDistrict?.id === d.id
                return (
                  <div
                    key={d.id}
                    onClick={() => selectDistrict(d)}
                    style={{
                      padding: 'var(--space-3) var(--space-4)',
                      borderBottom: '1px solid var(--border-default)',
                      cursor: 'pointer',
                      background: isSelected ? 'var(--color-primary-50)' : 'transparent',
                      borderLeft: isSelected ? '4px solid var(--color-primary-600)' : '4px solid transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'background 0.15s ease',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                        {d.name_en}{' '}
                        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                          ({d.code})
                        </span>
                      </div>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-primary-700)' }}>
                        {d.name_kn}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {d.is_active ? (
                        <span style={{ fontSize: 'var(--font-size-xs)', color: '#059669', fontWeight: 600 }}>
                          Active
                        </span>
                      ) : (
                        <span style={{ fontSize: 'var(--font-size-xs)', color: '#dc2626', fontWeight: 600 }}>
                          Inactive
                        </span>
                      )}
                      {isStateHead && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleDistrictStatus(d)
                          }}
                          style={{
                            fontSize: 10,
                            padding: '2px 6px',
                            borderRadius: 4,
                            border: '1px solid var(--border-default)',
                            background: 'var(--bg-subtle)',
                            cursor: 'pointer',
                          }}
                        >
                          {d.is_active ? 'Disable' : 'Enable'}
                        </button>
                      )}
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>

        {/* Talukas Detail Column */}
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
            <div>
              <h3 style={{ margin: 0, fontSize: 'var(--font-size-base)', fontWeight: 800 }}>
                {selectedDistrict ? `${selectedDistrict.name_en} Talukas` : 'Talukas'}
              </h3>
              <p style={{ margin: 0, fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                {talukas.length} administrative talukas in jurisdiction
              </p>
            </div>

            {isStateHead && selectedDistrict && (
              <button
                onClick={() => setShowAddTaluka(true)}
                className="btn btn-secondary"
                style={{ fontSize: 'var(--font-size-xs)', display: 'flex', alignItems: 'center', gap: 4 }}
              >
                <Plus size={14} /> Add Taluka
              </button>
            )}
          </div>

          <div style={{ padding: 'var(--space-4)' }}>
            {talukas.length === 0 ? (
              <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
                No talukas registered under this district yet.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 'var(--space-3)' }}>
                {talukas.map((t) => (
                  <div
                    key={t.id}
                    style={{
                      padding: 'var(--space-3)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-default)',
                      background: 'var(--bg-card)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 4,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <strong style={{ fontSize: 'var(--font-size-sm)' }}>{t.name_en}</strong>
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '1px 6px',
                          borderRadius: 999,
                          background: t.is_active ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                          color: t.is_active ? '#059669' : '#dc2626',
                        }}
                      >
                        {t.code}
                      </span>
                    </div>
                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                      {t.name_kn}
                    </div>

                    {isStateHead && (
                      <button
                        onClick={() => toggleTalukaStatus(t)}
                        style={{
                          marginTop: 'var(--space-2)',
                          padding: '3px 8px',
                          fontSize: 10,
                          fontWeight: 600,
                          borderRadius: 4,
                          border: '1px solid var(--border-default)',
                          background: 'var(--bg-subtle)',
                          cursor: 'pointer',
                          alignSelf: 'flex-start',
                        }}
                      >
                        Toggle Status ({t.is_active ? 'Active' : 'Disabled'})
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add District Modal */}
      {showAddDistrict && (
        <div className="modal-backdrop">
          <div className="modal" style={{ maxWidth: 460 }}>
            <h3 style={{ margin: '0 0 var(--space-4)' }}>Add New Karnataka District</h3>
            <form onSubmit={handleCreateDistrict} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div>
                <label className="label">District Name (English)</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. Vijayanagara"
                  value={newDistEn}
                  onChange={(e) => setNewDistEn(e.target.value)}
                />
              </div>
              <div>
                <label className="label">District Name (ಕನ್ನಡ)</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. ವಿಜಯನಗರ"
                  value={newDistKn}
                  onChange={(e) => setNewDistKn(e.target.value)}
                />
              </div>
              <div>
                <label className="label">District Code (2-5 letters)</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. VJN"
                  value={newDistCode}
                  onChange={(e) => setNewDistCode(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
                <button type="button" onClick={() => setShowAddDistrict(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create District
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Taluka Modal */}
      {showAddTaluka && selectedDistrict && (
        <div className="modal-backdrop">
          <div className="modal" style={{ maxWidth: 460 }}>
            <h3 style={{ margin: '0 0 var(--space-4)' }}>Add Taluka to {selectedDistrict.name_en}</h3>
            <form onSubmit={handleCreateTaluka} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div>
                <label className="label">Taluka Name (English)</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. Hospet"
                  value={newTalEn}
                  onChange={(e) => setNewTalEn(e.target.value)}
                />
              </div>
              <div>
                <label className="label">Taluka Name (ಕನ್ನಡ)</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. ಹೊಸಪೇಟೆ"
                  value={newTalKn}
                  onChange={(e) => setNewTalKn(e.target.value)}
                />
              </div>
              <div>
                <label className="label">Taluka Code</label>
                <input
                  required
                  className="input"
                  placeholder="e.g. HSP"
                  value={newTalCode}
                  onChange={(e) => setNewTalCode(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
                <button type="button" onClick={() => setShowAddTaluka(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Taluka
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
