import React, { useState } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'

export default function LoginScreen() {
  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const setAuth = useAuthStore((state) => state.setAuth)

  const handleSendOtp = async () => {
    if (!phone || phone.length < 10) {
      Alert.alert('Invalid Phone', 'Please enter a valid 10-digit mobile number')
      return
    }
    setLoading(true)
    try {
      // Phase 2 real OTP endpoint integration
      setTimeout(() => {
        setLoading(false)
        setStep('otp')
      }, 600)
    } catch {
      setLoading(false)
      Alert.alert('Error', 'Unable to send OTP. Please try again.')
    }
  }

  const handleVerifyOtp = async () => {
    if (!otp || otp.length !== 6) {
      Alert.alert('Invalid OTP', 'Please enter the 6-digit OTP')
      return
    }
    setLoading(true)
    try {
      setTimeout(() => {
        setLoading(false)
        // Login mock payload until Phase 2 backend verification is live
        setAuth(
          {
            id: 'mem-101',
            phone: `+91${phone}`,
            name: 'KPA Member',
            role: 'MEMBER',
            membership_no: 'KPA-BLR-0042',
            district: 'Bengaluru Urban',
            is_active: true,
          },
          'mock-jwt-token'
        )
      }, 600)
    } catch {
      setLoading(false)
      Alert.alert('Verification Failed', 'Invalid OTP entered')
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.header}>
        <Text style={styles.titleBadge}>KPA WELFARE</Text>
        <Text style={styles.headerTitle}>Karnataka Photography Association</Text>
        <Text style={styles.headerSubtitle}>
          ಕರ್ನಾಟಕ ಛಾಯಾಗ್ರಾಹಕರ ಸಂಘ (ರಿ.)
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>
          {step === 'phone' ? 'Member Login' : 'Enter 6-Digit OTP'}
        </Text>
        <Text style={styles.cardDesc}>
          {step === 'phone'
            ? 'Enter your registered mobile number to receive OTP'
            : `OTP sent to +91 ${phone}`}
        </Text>

        {step === 'phone' ? (
          <View style={styles.inputRow}>
            <Text style={styles.prefix}>+91</Text>
            <TextInput
              style={styles.input}
              placeholder="98765 43210"
              placeholderTextColor={colors.neutral.textMuted}
              keyboardType="phone-pad"
              maxLength={10}
              value={phone}
              onChangeText={setPhone}
            />
          </View>
        ) : (
          <TextInput
            style={[styles.input, styles.otpInput]}
            placeholder="• • • • • •"
            placeholderTextColor={colors.neutral.textMuted}
            keyboardType="number-pad"
            maxLength={6}
            value={otp}
            onChangeText={setOtp}
          />
        )}

        <TouchableOpacity
          style={styles.button}
          onPress={step === 'phone' ? handleSendOtp : handleVerifyOtp}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={colors.neutral.white} />
          ) : (
            <Text style={styles.buttonText}>
              {step === 'phone' ? 'Send OTP' : 'Verify & Continue'}
            </Text>
          )}
        </TouchableOpacity>

        {step === 'otp' && (
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => setStep('phone')}
          >
            <Text style={styles.backButtonText}>Change Mobile Number</Text>
          </TouchableOpacity>
        )}
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.primary[700],
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  titleBadge: {
    color: colors.gold[400],
    fontWeight: '800',
    letterSpacing: 2,
    fontSize: 12,
    marginBottom: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.neutral.white,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.75)',
    marginTop: 4,
    textAlign: 'center',
  },
  card: {
    backgroundColor: colors.neutral.white,
    borderRadius: 20,
    padding: 24,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 6,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.neutral.text,
  },
  cardDesc: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    marginTop: 4,
    marginBottom: 20,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: colors.neutral.border,
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 14,
    height: 52,
  },
  prefix: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.neutral.textSecondary,
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: colors.neutral.text,
    height: '100%',
  },
  otpInput: {
    textAlign: 'center',
    letterSpacing: 8,
    borderWidth: 1.5,
    borderColor: colors.neutral.border,
    borderRadius: 12,
    marginBottom: 16,
    height: 52,
    fontSize: 20,
    fontWeight: '700',
  },
  button: {
    backgroundColor: colors.primary[700],
    height: 52,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    color: colors.neutral.white,
    fontSize: 16,
    fontWeight: '700',
  },
  backButton: {
    marginTop: 14,
    alignItems: 'center',
  },
  backButtonText: {
    color: colors.primary[500],
    fontSize: 13,
    fontWeight: '600',
  },
})
