/**
 * Reports Page — Financial reports, membership growth, welfare settlements, and CSV data exports.
 */
import { useEffect, useState } from 'react'
import {
  Download,
  FileSpreadsheet,
  FileText,
  Heart,
} from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'react-toastify'

interface WelfareOption {
  id: string
  title: string
  deceased_member_name: string
}

export default function ReportsPage() {
  const [events, setEvents] = useState<WelfareOption[]>([])
  const [selectedEventId, setSelectedEventId] = useState<string>('')
  const [downloading, setDownloading] = useState<string | null>(null)

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const res = await api.get('/welfare-events')
        const evList: WelfareOption[] = res.data.data || []
        setEvents(evList)
        if (evList.length > 0) {
          setSelectedEventId(evList[0].id)
        }
      } catch {
        // Silently handled
      }
    }
    loadEvents()
  }, [])

  const handleDownloadCsv = async (endpoint: string, filename: string, key: string) => {
    setDownloading(key)
    try {
      const response = await api.get(endpoint, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success(`${filename} downloaded successfully`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg || 'Failed to download report. Verify permissions.')
    } finally {
      setDownloading(null)
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
          <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, margin: 0 }}>Reports & Master Data Exports</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            Direct export of official CSV ledgers, chartered accountant audit statements, and membership rolls.
          </p>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-6)',
        }}
      >
        {/* Member Master Roll */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 'var(--radius-md)',
                background: 'rgba(16, 185, 129, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileSpreadsheet size={22} color="#059669" />
            </div>
            <div>
              <h4 style={{ margin: 0, fontWeight: 700, fontSize: 'var(--font-size-base)' }}>Membership Master Roll</h4>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>Scoped by Jurisdiction</span>
            </div>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0, flex: 1 }}>
            Complete listing of all registered photographers, membership numbers, studio names, approval status, and taluka scopes.
          </p>
          <button
            onClick={() => handleDownloadCsv('/reports/members/csv', 'kpa_members_export.csv', 'members')}
            disabled={downloading === 'members'}
            className="btn btn-primary"
            style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <Download size={15} />
            {downloading === 'members' ? 'Exporting...' : 'Export Members CSV'}
          </button>
        </div>

        {/* Financial Audit Statement */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 'var(--radius-md)',
                background: 'rgba(37, 99, 235, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileText size={22} color="var(--color-primary-600)" />
            </div>
            <div>
              <h4 style={{ margin: 0, fontWeight: 700, fontSize: 'var(--font-size-base)' }}>Financial Audit Statement</h4>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>State Head & Auditor</span>
            </div>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0, flex: 1 }}>
            Full transaction ledger with gateway order IDs, cryptographic payment hashes, receipt numbers, and settlement timestamps.
          </p>
          <button
            onClick={() => handleDownloadCsv('/reports/financial/csv', 'kpa_financial_audit_statement.csv', 'financial')}
            disabled={downloading === 'financial'}
            className="btn btn-primary"
            style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
          >
            <Download size={15} />
            {downloading === 'financial' ? 'Exporting...' : 'Export Financial CSV'}
          </button>
        </div>

        {/* Welfare Event Ledger */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 'var(--radius-md)',
                background: 'rgba(239, 68, 68, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Heart size={22} color="var(--color-error-500)" />
            </div>
            <div>
              <h4 style={{ margin: 0, fontWeight: 700, fontSize: 'var(--font-size-base)' }}>Welfare Event Ledger</h4>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>Per-case debits</span>
            </div>
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: 0 }}>
            Debit obligation ledger for a specific welfare relief case showing member settlement status.
          </p>

          {events.length > 0 ? (
            <div style={{ marginTop: 'auto' }}>
              <label style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>
                Select Welfare Case:
              </label>
              <select
                className="input"
                value={selectedEventId}
                onChange={(e) => setSelectedEventId(e.target.value)}
                style={{ width: '100%', marginBottom: 'var(--space-3)', fontSize: 'var(--font-size-xs)' }}
              >
                {events.map((ev) => (
                  <option key={ev.id} value={ev.id}>
                    {ev.title} ({ev.deceased_member_name})
                  </option>
                ))}
              </select>
              <button
                onClick={() =>
                  handleDownloadCsv(
                    `/reports/welfare/${selectedEventId}/csv`,
                    `welfare_ledger_${selectedEventId}.csv`,
                    'welfare'
                  )
                }
                disabled={downloading === 'welfare' || !selectedEventId}
                className="btn btn-primary"
                style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
              >
                <Download size={15} />
                {downloading === 'welfare' ? 'Exporting...' : 'Export Welfare Ledger CSV'}
              </button>
            </div>
          ) : (
            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 'auto' }}>
              No active welfare events available to export.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
