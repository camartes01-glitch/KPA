import React, { useEffect, useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'
import { api } from '../services/api'

import { Ionicons } from '@expo/vector-icons'

export default function HomeScreen({ navigation }: any) {
  const { user, updateUser } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [pendingCount, setPendingCount] = useState(0)
  const [pendingDues, setPendingDues] = useState(0)
  const [activeEventsCount, setActiveEventsCount] = useState(0)

  const loadData = async () => {
    try {
      // 1. Fetch user obligations
      const obligationsRes = await api.get('/welfare-events/my-contributions')
      if (obligationsRes.data?.data) {
        const list: any[] = obligationsRes.data.data
        const pending = list.filter((c) => c.status === 'PENDING')
        setPendingCount(pending.length)
        const sum = pending.reduce((acc, c) => acc + (parseFloat(c.amount) || 10), 0)
        setPendingDues(sum)
      }

      // 2. Fetch active events count
      const eventsRes = await api.get('/welfare-events?status_filter=ACTIVE')
      if (eventsRes.data?.data) {
        setActiveEventsCount(eventsRes.data.data.length)
      }

      // 3. Fetch member details if membership_no missing
      if (!user?.membership_no) {
        try {
          const memberRes = await api.get('/members/me')
          if (memberRes.data?.data) {
            const m = memberRes.data.data
            updateUser({
              membership_no: m.membership_no,
              studio_name: m.studio_name,
              district: m.district_id ? String(m.district_id) : user?.district,
              status: m.status,
            })
          }
        } catch {
          // Member record might be created later
        }
      }
    } catch {
      // Handled gracefully for offline tolerance
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    loadData()
  }, [])

  const onRefresh = () => {
    setRefreshing(true)
    loadData()
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary[700]} />}
    >
      {/* Member Header Card */}
      <View style={styles.headerCard}>
        <View style={styles.badgeRow}>
          <Text style={styles.goldBadge}>
            {user?.is_active ? 'ACTIVE MEMBER' : 'REGISTERED MEMBER'}
          </Text>
          <View style={styles.headerIconsRow}>
            <Text style={styles.idText}>{user?.membership_no || 'KPA-MEMBER'}</Text>
            <TouchableOpacity
              onPress={() => navigation.navigate('Settings')}
              style={styles.gearButton}
              activeOpacity={0.7}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Ionicons name="settings-outline" size={18} color={colors.gold[400]} />
            </TouchableOpacity>
          </View>
        </View>
        <Text style={styles.memberName}>{user?.name || 'Photographer'}</Text>
        <Text style={styles.memberDistrict}>
          {user?.phone ? user.phone : ''} • {user?.role || 'MEMBER'}
        </Text>

        <TouchableOpacity
          style={styles.cardButton}
          onPress={() => navigation.navigate('DigitalCard')}
          activeOpacity={0.8}
        >
          <Text style={styles.cardButtonText}>View Digital ID Card & QR</Text>
        </TouchableOpacity>
      </View>

      {/* Welfare Status Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Mutual Welfare Status</Text>
        <View style={styles.statusBox}>
          <View style={styles.statusRow}>
            <View>
              <Text style={styles.statusLabel}>Pending Dues</Text>
              <Text style={styles.statusSub}>{pendingCount} case(s) pending settlement</Text>
            </View>
            <Text style={pendingDues > 0 ? styles.statusValDue : styles.statusValZero}>
              ₹{pendingDues.toFixed(2)}
            </Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.statusRow}>
            <View>
              <Text style={styles.statusLabel}>Active Emergency Relief Cases</Text>
              <Text style={styles.statusSub}>Statewide mutual benefit claims</Text>
            </View>
            <Text style={styles.statusActive}>{activeEventsCount}</Text>
          </View>
        </View>

        {pendingDues > 0 && (
          <TouchableOpacity
            style={styles.payPromptBtn}
            onPress={() => navigation.navigate('Welfare')}
            activeOpacity={0.85}
          >
            <Text style={styles.payPromptText}>
              Pay ₹{pendingDues.toFixed(2)} Pending Mutual Relief →
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Quick Action Grid */}
      <View style={styles.actionGrid}>
        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate('Welfare')}
          activeOpacity={0.8}
        >
          <Text style={styles.actionTitle}>Welfare Cases</Text>
          <Text style={styles.actionDesc}>View active claims & contribute</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate('Profile')}
          activeOpacity={0.8}
        >
          <Text style={styles.actionTitle}>My Profile</Text>
          <Text style={styles.actionDesc}>Verify nominee & KYC status</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.neutral.background,
  },
  content: {
    padding: 20,
  },
  headerCard: {
    backgroundColor: colors.primary[700],
    borderRadius: 20,
    padding: 22,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 4,
  },
  badgeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  goldBadge: {
    color: colors.gold[400],
    fontWeight: '800',
    fontSize: 11,
    letterSpacing: 1,
  },
  headerIconsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  gearButton: {
    padding: 4,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.12)',
  },
  idText: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 12,
    fontWeight: '600',
  },
  memberName: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.neutral.white,
    marginBottom: 4,
  },
  memberDistrict: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.75)',
    marginBottom: 20,
  },
  cardButton: {
    backgroundColor: colors.gold[400],
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  cardButtonText: {
    color: colors.primary[900],
    fontWeight: '700',
    fontSize: 14,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 12,
  },
  statusBox: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.neutral.text,
  },
  statusSub: {
    fontSize: 12,
    color: colors.neutral.textSecondary,
    marginTop: 2,
  },
  statusValZero: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.status.success,
  },
  statusValDue: {
    fontSize: 18,
    fontWeight: '800',
    color: '#dc2626',
  },
  statusActive: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.primary[700],
  },
  divider: {
    height: 1,
    backgroundColor: colors.neutral.border,
    marginVertical: 14,
  },
  payPromptBtn: {
    backgroundColor: '#dc2626',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  payPromptText: {
    color: colors.neutral.white,
    fontWeight: '700',
    fontSize: 14,
  },
  actionGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 4,
  },
  actionDesc: {
    fontSize: 12,
    color: colors.neutral.textSecondary,
    lineHeight: 16,
  },
})
