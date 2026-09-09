import React from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'

export default function HomeScreen({ navigation }: any) {
  const user = useAuthStore((state) => state.user)

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Member Header */}
      <View style={styles.headerCard}>
        <View style={styles.badgeRow}>
          <Text style={styles.goldBadge}>ACTIVE MEMBER</Text>
          <Text style={styles.idText}>{user?.membership_no || 'KPA-0000'}</Text>
        </View>
        <Text style={styles.memberName}>{user?.name || 'Photographer'}</Text>
        <Text style={styles.memberDistrict}>
          {user?.district || 'Karnataka State'} • Member
        </Text>

        <TouchableOpacity
          style={styles.cardButton}
          onPress={() => navigation.navigate('DigitalCard')}
        >
          <Text style={styles.cardButtonText}>View Digital ID Card & QR</Text>
        </TouchableOpacity>
      </View>

      {/* Welfare Status Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Welfare Fund Status</Text>
        <View style={styles.statusBox}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Pending Dues</Text>
            <Text style={styles.statusValZero}>₹0.00</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>AutoPay Status</Text>
            <Text style={styles.statusActive}>Configured</Text>
          </View>
        </View>
      </View>

      {/* Quick Action Buttons */}
      <View style={styles.actionGrid}>
        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate('Welfare')}
        >
          <Text style={styles.actionTitle}>Welfare Events</Text>
          <Text style={styles.actionDesc}>Active relief cases & history</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate('Profile')}
        >
          <Text style={styles.actionTitle}>My Nominee</Text>
          <Text style={styles.actionDesc}>Verify beneficiary details</Text>
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
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.3)',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
  },
  cardButtonText: {
    color: colors.neutral.white,
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
    padding: 18,
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  statusLabel: {
    fontSize: 14,
    color: colors.neutral.textSecondary,
    fontWeight: '500',
  },
  statusValZero: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.status.success,
  },
  statusActive: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.primary[500],
  },
  divider: {
    height: 1,
    backgroundColor: colors.neutral.border,
    marginVertical: 12,
  },
  actionGrid: {
    flexDirection: 'row',
    gap: 14,
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
    fontSize: 15,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 4,
  },
  actionDesc: {
    fontSize: 12,
    color: colors.neutral.textSecondary,
  },
})
