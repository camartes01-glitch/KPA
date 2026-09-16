import React, { useState, useEffect } from 'react'
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
import { api, checkBackendHealth, getErrorMessage, BASE_URL } from '../services/api'
export default function LoginScreen() {
  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [resending, setResending] = useState(false)
  const [cooldown, setCooldown] = useState(0)
  const [checkingHealth, setCheckingHealth] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [infoMessage, setInfoMessage] = useState<string | null>(null)
  const { setAuth, updateUser } = useAuthStore()

  useEffect(() => {
    let timer: any
    if (cooldown > 0) {
      timer = setInterval(() => {
        setCooldown((prev) => (prev > 0 ? prev - 1 : 0))
      }, 1000)
    }
    return () => {
      if (timer) clearInterval(timer)
    }
  }, [cooldown])

  const handleSendOtp = async () => {
    setErrorMessage(null)
    setInfoMessage(null)
    const cleaned = phone.replace(/\D/g, '')
    if (!cleaned || cleaned.length !== 10) {
      const msg = 'Please enter a valid 10-digit mobile number'
      setErrorMessage(msg)
      Alert.alert('Invalid Phone', msg)
      return
    }
    setLoading(true)
    try {
      const res = await api.post('/auth/otp/send', { phone: cleaned })
      const devCode = res.data?.data?.dev_code
      setStep('otp')
      setCooldown(30)
      const successMsg = devCode
        ? `OTP Sent! Verification code: ${devCode}`
        : 'OTP Sent! Please check your SMS for verification code.'
      setInfoMessage(successMsg)
      Alert.alert('OTP Sent', successMsg)
    } catch (err: any) {
      const msg = getErrorMessage(err)
      setErrorMessage(msg)
      Alert.alert('Unable to Send OTP', msg)
    } finally {
      setLoading(false)
    }
  }

  const handleResendOtp = async () => {
    if (cooldown > 0 || resending) return
    const cleaned = phone.replace(/\D/g, '')
    if (!cleaned || cleaned.length !== 10) {
      Alert.alert('Invalid Phone', 'Please enter a valid 10-digit mobile number')
      return
    }
    setResending(true)
    try {
      const res = await api.post('/auth/otp/send', { phone: cleaned })
      const devCode = res.data?.data?.dev_code
      setCooldown(30)
      if (devCode) {
        Alert.alert('OTP Resent', `Verification code: ${devCode}`)
      } else {
        Alert.alert('OTP Resent', 'A fresh OTP has been sent to your mobile number.')
      }
    } catch (err: any) {
      Alert.alert('Unable to Resend OTP', getErrorMessage(err))
    } finally {
      setResending(false)
    }
  }

  const handleVerifyOtp = async () => {
    const cleanedOtp = otp.trim()
    if (!cleanedOtp || cleanedOtp.length !== 6) {
      Alert.alert('Invalid OTP', 'Please enter the 6-digit OTP')
      return
    }
    setLoading(true)
    try {
      const cleanedPhone = phone.replace(/\D/g, '')
      const res = await api.post('/auth/otp/verify', {
        phone: cleanedPhone,
        otp: cleanedOtp,
        device_name: `${Platform.OS} Mobile App`,
      })
      const { user, access_token, refresh_token } = res.data.data
      setAuth(user, access_token, refresh_token)

      // Fetch enriched member profile in background
      try {
        const memberRes = await api.get('/members/me', {
          headers: { Authorization: `Bearer ${access_token}` },
        })
        if (memberRes.data?.data) {
          const m = memberRes.data.data
          updateUser({
            membership_no: m.membership_no,
            studio_name: m.studio_name,
            status: m.status,
          })
        }
      } catch {
        // Fallback to basic user profile if member record is pending
      }
    } catch (err: any) {
      Alert.alert('Verification Failed', getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const handleCheckHealth = async () => {
    setCheckingHealth(true)
    try {
      const res = await checkBackendHealth()
      if (res.ok) {
        Alert.alert(
          'Server Connected',
          `Successfully reached KPA Welfare server:\n${BASE_URL}\n\nStatus: ${res.data?.status || 'OK'}`
        )
      } else {
        Alert.alert(
          'Connection Failed',
          `Could not connect to:\n${BASE_URL}\n\n${res.error}\n\nPlease check your internet connection or server availability.`
        )
      }
    } finally {
      setCheckingHealth(false)
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

        {typeof __DEV__ !== 'undefined' && __DEV__ && (
          <TouchableOpacity
            style={styles.demoBanner}
            onPress={() => {
              if (step === 'phone') setPhone('9900000004')
              else setOtp('123456')
            }}
            activeOpacity={0.8}
          >
            <Text style={styles.demoBannerText}>
              ⚙️ LOCAL DEMO MODE: Tap to fill demo {step === 'phone' ? 'phone (9900000004)' : 'OTP (123456)'}
            </Text>
          </TouchableOpacity>
        )}

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

        {errorMessage ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorBoxText}>{errorMessage}</Text>
          </View>
        ) : null}

        {infoMessage ? (
          <View style={styles.infoBox}>
            <Text style={styles.infoBoxText}>{infoMessage}</Text>
          </View>
        ) : null}

        <TouchableOpacity
          style={styles.button}
          onPress={step === 'phone' ? handleSendOtp : handleVerifyOtp}
          disabled={loading}
          activeOpacity={0.8}
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
          <View style={styles.otpActionRow}>
            <TouchableOpacity
              style={styles.resendButton}
              onPress={handleResendOtp}
              disabled={cooldown > 0 || resending}
              activeOpacity={0.7}
            >
              {resending ? (
                <ActivityIndicator size="small" color={colors.primary[700]} />
              ) : (
                <Text
                  style={[
                    styles.resendButtonText,
                    cooldown > 0 && styles.resendDisabledText,
                  ]}
                >
                  {cooldown > 0 ? `Resend OTP in ${cooldown}s` : 'Resend OTP'}
                </Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.backButton}
              onPress={() => setStep('phone')}
              activeOpacity={0.7}
            >
              <Text style={styles.backButtonText}>Change Number</Text>
            </TouchableOpacity>
          </View>
        )}

        <TouchableOpacity
          style={styles.healthButton}
          onPress={handleCheckHealth}
          disabled={checkingHealth}
          activeOpacity={0.7}
        >
          {checkingHealth ? (
            <ActivityIndicator size="small" color={colors.primary[500]} />
          ) : (
            <Text style={styles.healthButtonText}>Check Server Connection</Text>
          )}
        </TouchableOpacity>
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
    marginBottom: 16,
  },
  demoBanner: {
    backgroundColor: '#fef3c7',
    borderWidth: 1,
    borderColor: '#f59e0b',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginBottom: 16,
  },
  demoBannerText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#92400e',
    textAlign: 'center',
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
  otpActionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 14,
    paddingHorizontal: 4,
  },
  resendButton: {
    paddingVertical: 6,
    paddingHorizontal: 8,
  },
  resendButtonText: {
    color: colors.primary[700],
    fontSize: 13,
    fontWeight: '700',
  },
  resendDisabledText: {
    color: colors.neutral.textMuted,
    fontWeight: '500',
  },
  backButton: {
    paddingVertical: 6,
    paddingHorizontal: 8,
  },
  backButtonText: {
    color: colors.neutral.textSecondary,
    fontSize: 13,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  healthButton: {
    marginTop: 18,
    alignItems: 'center',
    paddingVertical: 6,
  },
  healthButtonText: {
    color: colors.neutral.textSecondary,
    fontSize: 12,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
  errorBox: {
    backgroundColor: '#fee2e2',
    borderColor: '#fca5a5',
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
  },
  errorBoxText: {
    color: '#991b1b',
    fontSize: 13,
    fontWeight: '600',
    textAlign: 'center',
  },
  infoBox: {
    backgroundColor: '#dbeafe',
    borderColor: '#93c5fd',
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
  },
  infoBoxText: {
    color: '#1e40af',
    fontSize: 13,
    fontWeight: '600',
    textAlign: 'center',
  },
})
