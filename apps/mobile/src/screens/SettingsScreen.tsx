import React, { useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'
import { checkBackendHealth, getErrorMessage, BASE_URL } from '../services/api'

export default function SettingsScreen({ navigation }: any) {
  const { user, logout } = useAuthStore()
  const [checking, setChecking] = useState(false)
  const [pingResult, setPingResult] = useState<{
    ok: boolean
    latencyMs?: number
    message?: string
  } | null>(null)
  const [language, setLanguage] = useState<'en' | 'kn'>('en')

  const handleTestConnection = async () => {
    setChecking(true)
    setPingResult(null)
    const start = Date.now()
    try {
      const res = await checkBackendHealth()
      const latency = Date.now() - start
      if (res.ok) {
        setPingResult({
          ok: true,
          latencyMs: latency,
          message: `Connected (${latency} ms)`,
        })
      } else {
        setPingResult({
          ok: false,
          message: res.error || 'Server unreachable',
        })
      }
    } catch (err: any) {
      setPingResult({
        ok: false,
        message: getErrorMessage(err),
      })
    } finally {
      setChecking(false)
    }
  }

  const handleConfirmLogout = () => {
    Alert.alert(
      'Log Out',
      'Are you sure you want to log out from this device?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Log Out',
          style: 'destructive',
          onPress: () => {
            logout()
          },
        },
      ],
      { cancelable: true }
    )
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Association Header */}
      <View style={styles.headerBox}>
        <Text style={styles.headerTitle}>Settings & Diagnostics</Text>
        <Text style={styles.headerSub}>KPA Member Mobile App v1.0.0</Text>
      </View>

      {/* Backend Connectivity Card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="server-outline" size={20} color={colors.primary[700]} />
          <Text style={styles.cardTitle}>Backend Server Connection</Text>
        </View>
        <Text style={styles.urlText}>{BASE_URL}</Text>

        <TouchableOpacity
          style={styles.pingButton}
          onPress={handleTestConnection}
          disabled={checking}
          activeOpacity={0.8}
        >
          {checking ? (
            <ActivityIndicator size="small" color={colors.neutral.white} />
          ) : (
            <Text style={styles.pingButtonText}>Test Server Connection</Text>
          )}
        </TouchableOpacity>

        {pingResult && (
          <View
            style={[
              styles.resultBox,
              pingResult.ok ? styles.resultBoxOk : styles.resultBoxError,
            ]}
          >
            <Ionicons
              name={pingResult.ok ? 'checkmark-circle' : 'alert-circle'}
              size={18}
              color={pingResult.ok ? '#16a34a' : '#dc2626'}
            />
            <Text
              style={[
                styles.resultText,
                pingResult.ok ? styles.resultTextOk : styles.resultTextError,
              ]}
            >
              {pingResult.message}
            </Text>
          </View>
        )}
      </View>

      {/* Language Preference */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="language-outline" size={20} color={colors.primary[700]} />
          <Text style={styles.cardTitle}>Language / ಭಾಷೆ</Text>
        </View>
        <View style={styles.langRow}>
          <TouchableOpacity
            style={[styles.langOption, language === 'en' && styles.langOptionActive]}
            onPress={() => setLanguage('en')}
            activeOpacity={0.8}
          >
            <Text
              style={[
                styles.langOptionText,
                language === 'en' && styles.langOptionTextActive,
              ]}
            >
              English
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.langOption, language === 'kn' && styles.langOptionActive]}
            onPress={() => setLanguage('kn')}
            activeOpacity={0.8}
          >
            <Text
              style={[
                styles.langOptionText,
                language === 'kn' && styles.langOptionTextActive,
              ]}
            >
              ಕನ್ನಡ (Kannada)
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Member Session Info */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="shield-checkmark-outline" size={20} color={colors.primary[700]} />
          <Text style={styles.cardTitle}>Active Session Details</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Logged-In Phone:</Text>
          <Text style={styles.infoVal}>{user?.phone || 'N/A'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Member Name:</Text>
          <Text style={styles.infoVal}>{user?.name || 'Photographer'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Membership No:</Text>
          <Text style={styles.infoVal}>{user?.membership_no || 'Allocated on Verification'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Role & Jurisdiction:</Text>
          <Text style={styles.infoVal}>{user?.role || 'MEMBER'} • Karnataka</Text>
        </View>
      </View>

      {/* Association Legal & About */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="information-circle-outline" size={20} color={colors.primary[700]} />
          <Text style={styles.cardTitle}>About Association</Text>
        </View>
        <Text style={styles.aboutText}>
          Karnataka Photography Association (Reg. No. 42/1986). Official statewide mutual benefit and professional organization protecting working photographers across all 31 districts of Karnataka.
        </Text>
      </View>

      {/* Logout Action */}
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleConfirmLogout}
        activeOpacity={0.8}
      >
        <Ionicons name="log-out-outline" size={18} color="#dc2626" />
        <Text style={styles.logoutText}>Log Out from KPA App</Text>
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
    paddingBottom: 40,
  },
  headerBox: {
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.neutral.text,
  },
  headerSub: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    marginTop: 2,
  },
  card: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.neutral.border,
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.neutral.text,
  },
  urlText: {
    fontSize: 12,
    color: colors.neutral.textSecondary,
    marginBottom: 12,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
  },
  pingButton: {
    backgroundColor: colors.primary[700],
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  pingButtonText: {
    color: colors.neutral.white,
    fontWeight: '700',
    fontSize: 13,
  },
  resultBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 12,
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
  },
  resultBoxOk: {
    backgroundColor: '#dcfce7',
    borderColor: '#86efac',
  },
  resultBoxError: {
    backgroundColor: '#fee2e2',
    borderColor: '#fca5a5',
  },
  resultText: {
    fontSize: 13,
    fontWeight: '600',
  },
  resultTextOk: {
    color: '#15803d',
  },
  resultTextError: {
    color: '#b91c1c',
  },
  langRow: {
    flexDirection: 'row',
    gap: 12,
  },
  langOption: {
    flex: 1,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.neutral.border,
    borderRadius: 10,
    alignItems: 'center',
  },
  langOptionActive: {
    borderColor: colors.primary[700],
    backgroundColor: colors.primary[50],
  },
  langOptionText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.neutral.textSecondary,
  },
  langOptionTextActive: {
    color: colors.primary[700],
    fontWeight: '700',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.neutral.border,
  },
  infoLabel: {
    fontSize: 12,
    color: colors.neutral.textSecondary,
  },
  infoVal: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.neutral.text,
  },
  aboutText: {
    fontSize: 13,
    lineHeight: 18,
    color: colors.neutral.textSecondary,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#fee2e2',
    borderWidth: 1,
    borderColor: '#fecaca',
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 8,
  },
  logoutText: {
    color: '#dc2626',
    fontWeight: '700',
    fontSize: 15,
  },
})
