import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import MembersPage from '@/pages/MembersPage'
import WelfareEventsPage from '@/pages/WelfareEventsPage'
import PaymentsPage from '@/pages/PaymentsPage'
import ReceiptsPage from '@/pages/ReceiptsPage'
import NotificationsPage from '@/pages/NotificationsPage'
import ReportsPage from '@/pages/ReportsPage'
import AuditLogsPage from '@/pages/AuditLogsPage'
import RolesPage from '@/pages/RolesPage'
import DistrictsPage from '@/pages/DistrictsPage'
import CommitteesPage from '@/pages/CommitteesPage'
import SettingsPage from '@/pages/SettingsPage'
import ForbiddenPage from '@/pages/ForbiddenPage'
import AppLayout from '@/layouts/AppLayout'

function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode
  allowedRoles?: string[]
}) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/403" replace />
  }
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route
          path="/login"
          element={<PublicRoute><LoginPage /></PublicRoute>}
        />

        {/* 403 Forbidden */}
        <Route
          path="/403"
          element={<ProtectedRoute><ForbiddenPage /></ProtectedRoute>}
        />

        {/* Protected — inside layout */}
        <Route
          path="/"
          element={<ProtectedRoute><AppLayout /></ProtectedRoute>}
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route
            path="members"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'DISTRICT_ADMIN', 'TALUKA_ADMIN', 'AUDITOR']}>
                <MembersPage />
              </ProtectedRoute>
            }
          />
          <Route path="welfare-events" element={<WelfareEventsPage />} />
          <Route
            path="payments"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'DISTRICT_ADMIN', 'TALUKA_ADMIN', 'AUDITOR']}>
                <PaymentsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="receipts"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'DISTRICT_ADMIN', 'TALUKA_ADMIN', 'AUDITOR', 'MEMBER']}>
                <ReceiptsPage />
              </ProtectedRoute>
            }
          />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route
            path="reports"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'DISTRICT_ADMIN', 'TALUKA_ADMIN', 'AUDITOR']}>
                <ReportsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="audit-logs"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'AUDITOR']}>
                <AuditLogsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="roles"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'DISTRICT_ADMIN']}>
                <RolesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="districts"
            element={
              <ProtectedRoute allowedRoles={['STATE_HEAD', 'DISTRICT_ADMIN']}>
                <DistrictsPage />
              </ProtectedRoute>
            }
          />
          <Route path="committees" element={<CommitteesPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
