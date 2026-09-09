import React from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'

export default function ProfileScreen() {
  const { user, logout } = useAuthStore()

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Member Profile</Text>

      <View style={styles.card}>
        <View style={styles.field}>
          <Text style={styles.label}>Full Name</Text>
          <Text style={styles.value}>{user?.name || 'Photographer'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Phone Number</Text>
          <Text style={styles.value}>{user?.phone || '+91 98765 43210'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Membership ID</Text>
          <Text style={styles.value}>{user?.membership_no || 'KPA-BLR-0042'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>District</Text>
          <Text style={styles.value}>{user?.district || 'Bengaluru Urban'}</Text>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>KYC Status</Text>
          <Text style={styles.kycApproved}>Verified & Approved</Text>
        </View>
      </View>

      <Text style={[styles.heading, { marginTop: 24 }]}>Nominee Information</Text>
      <View style={styles.card}>
        <View style={styles.field}>
          <Text style={styles.label}>Primary Nominee</Text>
          <Text style={styles.value}>Designated Family Member</Text>
        </View>
        <View style={styles.field}>
          <Text style={styles.label}>Relationship</Text>
          <Text style={styles.value}>Spouse</Text>
        </View>
        <View style={styles.field}>
          <Text style={styles.label}>Bank Account Status</Text>
          <Text style={styles.kycApproved}>Aadhaar Linked</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={logout}>
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
  heading: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.neutral.text,
    marginBottom: 12,
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
  kycApproved: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.status.success,
    marginTop: 2,
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
