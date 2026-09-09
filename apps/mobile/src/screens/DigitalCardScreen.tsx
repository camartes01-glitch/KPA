import React from 'react'
import { View, Text, StyleSheet, ScrollView } from 'react-native'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'

export default function DigitalCardScreen() {
  const user = useAuthStore((state) => state.user)

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Physical-style Card */}
      <View style={styles.idCard}>
        {/* Top Header */}
        <View style={styles.cardHeader}>
          <Text style={styles.kpaState}>KARNATAKA PHOTOGRAPHY ASSOCIATION</Text>
          <Text style={styles.kpaKannada}>ಕರ್ನಾಟಕ ಛಾಯಾಗ್ರಾಹಕರ ಸಂಘ (ರಿ.)</Text>
          <Text style={styles.idCardTitle}>DIGITAL MEMBERSHIP IDENTITY CARD</Text>
        </View>

        {/* Card Body */}
        <View style={styles.cardBody}>
          <View style={styles.photoPlaceholder}>
            <Text style={styles.photoText}>PHOTO</Text>
          </View>

          <View style={styles.memberInfo}>
            <Text style={styles.label}>MEMBER NAME</Text>
            <Text style={styles.valName}>{user?.name || 'Photographer'}</Text>

            <Text style={styles.label}>MEMBERSHIP ID</Text>
            <Text style={styles.valId}>{user?.membership_no || 'KPA-BLR-0042'}</Text>

            <Text style={styles.label}>DISTRICT / TALUKA</Text>
            <Text style={styles.valText}>{user?.district || 'Bengaluru Urban'}</Text>

            <Text style={styles.label}>MOBILE NUMBER</Text>
            <Text style={styles.valText}>{user?.phone || '+91 98765 43210'}</Text>
          </View>
        </View>

        {/* QR Verification Placeholder */}
        <View style={styles.qrContainer}>
          <View style={styles.qrPlaceholder}>
            <Text style={styles.qrText}>QR CODE</Text>
            <Text style={styles.qrSub}>Official KPA Digital Signature</Text>
          </View>
        </View>

        <View style={styles.cardFooter}>
          <Text style={styles.footerNote}>
            Valid Statewide across all 31 Districts • Registered Association
          </Text>
        </View>
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
    alignItems: 'center',
  },
  idCard: {
    width: '100%',
    backgroundColor: colors.primary[700],
    borderRadius: 20,
    padding: 20,
    borderWidth: 2,
    borderColor: colors.gold[400],
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
  },
  cardHeader: {
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.2)',
    paddingBottom: 12,
    marginBottom: 16,
  },
  kpaState: {
    color: colors.gold[400],
    fontWeight: '800',
    fontSize: 13,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  kpaKannada: {
    color: 'rgba(255,255,255,0.85)',
    fontSize: 12,
    textAlign: 'center',
    marginVertical: 2,
  },
  idCardTitle: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 1,
    marginTop: 4,
  },
  cardBody: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 16,
  },
  photoPlaceholder: {
    width: 90,
    height: 110,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  photoText: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 11,
    fontWeight: '700',
  },
  memberInfo: {
    flex: 1,
  },
  label: {
    fontSize: 9,
    fontWeight: '700',
    color: colors.gold[400],
    letterSpacing: 0.5,
  },
  valName: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.neutral.white,
    marginBottom: 6,
  },
  valId: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.neutral.white,
    marginBottom: 6,
  },
  valText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.9)',
    marginBottom: 6,
  },
  qrContainer: {
    alignItems: 'center',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.15)',
  },
  qrPlaceholder: {
    backgroundColor: colors.neutral.white,
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  qrText: {
    fontWeight: '800',
    fontSize: 13,
    color: colors.primary[700],
  },
  qrSub: {
    fontSize: 10,
    color: colors.neutral.textSecondary,
    marginTop: 2,
  },
  cardFooter: {
    marginTop: 8,
    alignItems: 'center',
  },
  footerNote: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.6)',
    textAlign: 'center',
  },
})
