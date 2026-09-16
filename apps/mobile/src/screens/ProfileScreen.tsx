import React, { useEffect, useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'
import { api } from '../services/api'

interface Nominee {
  name: string
  relationship_to_member: string
  phone?: string
  bank_account_no?: string
  bank_ifsc?: string
  bank_name?: string
  is_primary?: boolean
}

interface MemberProfile {
  id: string
  membership_no?: string
  full_name: string
  status: string
  studio_name?: string
  experience_years?: number
  district_id?: string
  nominees: Nominee[]
}

export default function ProfileScreen({ navigation }: any) {
  const { user, logout, updateUser } = useAuthStore()
  const [profile, setProfile] = useState<MemberProfile | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const fetchProfile = async () => {
    try {
      const res = await api.get('/members/me')
      if (res.data?.success && res.data?.data) {
        const m = res.data.data
        setProfile(m)
        updateUser({
          membership_no: m.membership_no,
          name: m.full_name,
          studio_name: m.studio_name,
          status: m.status,
        })
      }
    } catch {
      // If member profile registration is pending, gracefully fallback to auth user details
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    fetchProfile()
  }, [])

  const onRefresh = () => {
    setRefreshing(true)
    fetchProfile()
  }

  const handleLogout = () => {
    Alert.alert(
      'Confirm Log Out',
      'Are you sure you want to log out of your KPA Member account?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Log Out',
          style: 'destructive',
          onPress: () => logout(),
        },
      ]
    )
  }

  const primaryNominee = profile?.nominees?.find((n) => n.is_primary) || profile?.nominees?.[0]
  const memberStatus = profile?.status || (user?.is_active ? 'ACTIVE' : 'PENDING_APPROVAL')

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor={colors.primary[700]}
        />
      }
    >
      <View style={styles.headerRow}>
        <Text style={styles.heading}>Member Profile</Text>
        {loading && <ActivityIndicator size="small" color={colors.primary[700]} />}
      </View>

      <View style={styles.card}>
        <View style={styles.field}>
          <Text style={styles.label}>Full Name</Text>
          <Text style={styles.value}>{profile?.full_name || user?.name || 'Photographer'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Phone Number</Text>
          <Text style={styles.value}>{user?.phone || 'Not Provided'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Membership ID</Text>
          <Text style={styles.value}>
            {profile?.membership_no || user?.membership_no || 'Pending Allocation'}
          </Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Studio / Business Name</Text>
          <Text style={styles.value}>{profile?.studio_name || 'Individual Freelance'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>District / Location</Text>
          <Text style={styles.value}>{user?.district || 'Karnataka'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Verification Status</Text>
          <Text
            style={[
              styles.statusBadge,
              memberStatus === 'APPROVED' || memberStatus === 'ACTIVE'
                ? styles.statusApproved
                : styles.statusPending,
            ]}
          >
            {memberStatus === 'APPROVED' || memberStatus === 'ACTIVE'
              ? '● Verified & Active'
              : `● ${memberStatus.replace('_', ' ')}`}
          </Text>
        </View>
      </View>

      <Text style={[styles.heading, { marginTop: 24 }]}>Nominee Information</Text>
      <View style={styles.card}>
        {primaryNominee ? (
          <>
            <View style={styles.field}>
              <Text style={styles.label}>Primary Nominee</Text>
              <Text style={styles.value}>{primaryNominee.name}</Text>
            </View>
            <View style={styles.field}>
              <Text style={styles.label}>Relationship</Text>
              <Text style={styles.value}>{primaryNominee.relationship_to_member}</Text>
            </View>
            <View style={styles.field}>
              <Text style={styles.label}>Nominee Phone</Text>
              <Text style={styles.value}>{primaryNominee.phone || 'N/A'}</Text>
            </View>
            <View style={styles.field}>
              <Text style={styles.label}>Bank Account Status</Text>
              <Text style={styles.statusApproved}>
                {primaryNominee.bank_account_no
                  ? `Linked (${primaryNominee.bank_name || 'Bank'} - ${primaryNominee.bank_ifsc || 'IFSC Registered'})`
                  : 'Pending Bank Linking'}
              </Text>
            </View>
          </>
        ) : (
          <View style={styles.emptyNominee}>
            <Text style={styles.emptyText}>
              No nominee registered yet. Update your registration in the portal or contact your district admin.
            </Text>
          </View>
        )}
      </View>

      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}
        activeOpacity={0.8}
      >
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  heading: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.neutral.text,
  },
  card: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  field: {
    marginBottom: 12,
  },
  label: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.neutral.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  value: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.neutral.text,
    marginTop: 2,
  },
  statusBadge: {
    fontSize: 13,
    fontWeight: '700',
    marginTop: 2,
  },
  statusApproved: {
    color: '#16a34a',
  },
  statusPending: {
    color: '#d97706',
  },
  emptyNominee: {
    paddingVertical: 8,
  },
  emptyText: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    lineHeight: 18,
  },
  logoutButton: {
    marginTop: 32,
    backgroundColor: '#fee2e2',
    borderWidth: 1,
    borderColor: '#fecaca',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  logoutText: {
    color: '#dc2626',
    fontWeight: '700',
    fontSize: 15,
  },
})
