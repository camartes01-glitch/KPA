/**
 * AppLayout — sidebar + topbar shell for the admin panel.
 */
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  LayoutDashboard, Users, Heart, CreditCard, Bell,
  BarChart3, Shield, UserCheck, Settings, LogOut, Menu, X,
  ChevronRight
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'

const navItems = [
  { to: '/dashboard',     icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/members',       icon: Users,            label: 'Members' },
  { to: '/welfare-events',icon: Heart,            label: 'Welfare Events' },
  { to: '/payments',      icon: CreditCard,       label: 'Payments' },
  { to: '/notifications', icon: Bell,             label: 'Notifications' },
  { to: '/reports',       icon: BarChart3,        label: 'Reports' },
  { to: '/audit-logs',    icon: Shield,           label: 'Audit Logs',    roles: ['STATE_HEAD'] },
  { to: '/roles',         icon: UserCheck,        label: 'Role Management', roles: ['STATE_HEAD', 'DISTRICT_ADMIN'] },
  { to: '/settings',      icon: Settings,         label: 'Settings' },
]

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
    } catch {
      // Proceed with local logout regardless
    }
    logout()
    navigate('/login')
  }

  const visibleItems = navItems.filter(item =>
    !item.roles || (user && item.roles.includes(user.role))
  )

  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <aside
        className="sidebar"
        style={{
          width: collapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)',
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          background: 'var(--bg-sidebar)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width var(--transition-normal)',
          zIndex: 100,
          overflow: 'hidden',
        }}
      >
        {/* Logo + collapse toggle */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          padding: 'var(--space-4) var(--space-4)',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          minHeight: 'var(--topbar-height)',
        }}>
          {!collapsed && (
            <div>
              <div style={{ color: 'var(--color-gold-400)', fontWeight: 700, fontSize: 'var(--font-size-lg)' }}>
                KPA Welfare
              </div>
              <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 'var(--font-size-xs)' }}>
                Admin Panel
              </div>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'rgba(255,255,255,0.7)',
              cursor: 'pointer',
              padding: 'var(--space-1)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
            }}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <Menu size={20} /> : <X size={20} />}
          </button>
        </div>

        {/* Nav links */}
        <nav style={{ flex: 1, padding: 'var(--space-4) var(--space-2)', overflowY: 'auto' }}>
          {visibleItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              title={collapsed ? label : undefined}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-3)',
                padding: 'var(--space-3) var(--space-3)',
                borderRadius: 'var(--radius-md)',
                marginBottom: 'var(--space-1)',
                color: isActive ? 'white' : 'rgba(255,255,255,0.65)',
                background: isActive ? 'rgba(255,255,255,0.12)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: 'var(--font-size-sm)',
                textDecoration: 'none',
                transition: 'all var(--transition-fast)',
                whiteSpace: 'nowrap',
              })}
            >
              <Icon size={18} style={{ flexShrink: 0 }} />
              {!collapsed && <span>{label}</span>}
              {!collapsed && <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.4 }} />}
            </NavLink>
          ))}
        </nav>

        {/* User info + logout */}
        <div style={{
          padding: 'var(--space-4)',
          borderTop: '1px solid rgba(255,255,255,0.1)',
        }}>
          {!collapsed && (
            <div style={{ marginBottom: 'var(--space-3)' }}>
              <div style={{ color: 'white', fontWeight: 600, fontSize: 'var(--font-size-sm)' }}>
                {user?.name || 'User'}
              </div>
              <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 'var(--font-size-xs)' }}>
                {user?.role?.replace('_', ' ')}
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-2)',
              width: '100%',
              padding: 'var(--space-2) var(--space-3)',
              background: 'rgba(239,68,68,0.15)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 'var(--radius-md)',
              color: '#fca5a5',
              cursor: 'pointer',
              fontSize: 'var(--font-size-sm)',
              justifyContent: collapsed ? 'center' : 'flex-start',
            }}
          >
            <LogOut size={16} />
            {!collapsed && 'Logout'}
          </button>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────────── */}
      <div
        style={{
          marginLeft: collapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          transition: 'margin-left var(--transition-normal)',
        }}
      >
        {/* Topbar */}
        <header style={{
          height: 'var(--topbar-height)',
          background: 'var(--bg-surface)',
          borderBottom: '1px solid var(--border-default)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 var(--space-6)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          boxShadow: 'var(--shadow-sm)',
        }}>
          <div style={{ flex: 1 }} />
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-4)',
          }}>
            <div style={{
              background: 'var(--color-primary-700)',
              color: 'white',
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: 'var(--font-size-sm)',
            }}>
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main style={{ flex: 1, padding: 'var(--space-6)' }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
