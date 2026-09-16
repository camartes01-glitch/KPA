import React, { useEffect, useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  Image,
} from 'react-native'
import QRCode from 'react-native-qrcode-svg'
import { colors } from '../theme/colors'
import { useAuthStore } from '../store/authStore'
import { api } from '../services/api'

interface DigitalCardData {
  member_id: string
  membership_no: string
  full_name: string
  photo_url?: string | null
  qr_data: string
  valid_until?: string | null
  status: string
}

export default function DigitalCardScreen() {
  const { user, updateUser } = useAuthStore()
  const [cardData, setCardData] = useState<DigitalCardData | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const fetchCard = async () => {
    try {
      const res = await api.get('/members/me/card')
      if (res.data?.success && res.data?.data) {
        const data: DigitalCardData = res.data.data
        setCardData(data)
        if (data.membership_no && data.membership_no !== user?.membership_no) {
          updateUser({
            membership_no: data.membership_no,
            name: data.full_name || user?.name,
            status: data.status,
          })
        }
      }
    } catch {
      // If card endpoint is pending registration, fallback to user profile
      try {
        const profileRes = await api.get('/members/me')
        if (profileRes.data?.data) {
          const m = profileRes.data.data
          updateUser({
            membership_no: m.membership_no,
            name: m.full_name,
            studio_name: m.studio_name,
            status: m.status,
          })
        }
      } catch {
        // Safe offline tolerance
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    fetchCard()
  }, [])

  const onRefresh = () => {
    setRefreshing(true)
    fetchCard()
  }

  const membershipNo = cardData?.membership_no || user?.membership_no || 'KPA-PENDING'
  const memberName = cardData?.full_name || user?.name || 'Registered Member'
  const memberStatus = cardData?.status || (user?.is_active ? 'APPROVED' : 'PENDING_APPROVAL')

  // Real verification payload encoded into the QR
  const qrValue =
    cardData?.qr_data ||
    JSON.stringify({
      association: 'KARNATAKA PHOTOGRAPHY ASSOCIATION',
      reg_no: '42/1986',
      member_id: cardData?.member_id || user?.id || 'PENDING',
      membership_no: membershipNo,
      name: memberName,
      phone: user?.phone || '',
      district: user?.district || 'Karnataka',
      status: memberStatus,
      verify_url: `https://kpawelfare.org/verify/${membershipNo}`,
    })

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
      {loading && !cardData && (
        <ActivityIndicator
          size="small"
          color={colors.primary[700]}
          style={{ marginBottom: 12 }}
        />
      )}

      {/* Physical-style Card */}
      <View style={styles.idCard}>
        {/* Top Header */}
        <View style={styles.cardHeader}>
          <Text style={styles.kpaState}>KARNATAKA PHOTOGRAPHY ASSOCIATION</Text>
          <Text style={styles.kpaKannada}>ಕರ್ನಾಟಕ ಛಾಯಾಗ್ರಾಹಕರ ಸಂಘ (ರಿ.)</Text>
          <Text style={styles.idCardTitle}>OFFICIAL DIGITAL MEMBERSHIP PASS</Text>
        </View>

        {/* Card Body */}
        <View style={styles.cardBody}>
          <View style={styles.photoPlaceholder}>
            {cardData?.photo_url ? (
              <Image
                source={{ uri: cardData.photo_url }}
                style={styles.photoImage}
                resizeMode="cover"
              />
            ) : (
              <>
                <Text style={styles.photoText}>KPA</Text>
                <Text style={styles.photoSubText}>OFFICIAL</Text>
              </>
            )}
          </View>

          <View style={styles.memberInfo}>
            <Text style={styles.label}>MEMBER NAME</Text>
            <Text style={styles.valName}>{memberName}</Text>

            <Text style={styles.label}>MEMBERSHIP ID</Text>
            <Text style={styles.valId}>{membershipNo}</Text>

            <Text style={styles.label}>DISTRICT / TALUKA</Text>
            <Text style={styles.valText}>
              {user?.district
                ? `${user.district}${user.taluka ? ` / ${user.taluka}` : ''}`
                : 'Karnataka Statewide'}
            </Text>

            <Text style={styles.label}>REGISTERED PHONE</Text>
            <Text style={styles.valText}>{user?.phone || 'Not Provided'}</Text>

            <Text style={styles.label}>STATUS</Text>
            <View style={styles.badgeContainer}>
              <Text
                style={
                  memberStatus === 'APPROVED' || user?.is_active
                    ? styles.statusActive
                    : styles.statusPending
                }
              >
                {memberStatus === 'APPROVED' || user?.is_active
                  ? '● ACTIVE & VERIFIED'
                  : '● PENDING VERIFICATION'}
              </Text>
            </View>
          </View>
        </View>

        {/* Real QR Verification */}
        <View style={styles.qrContainer}>
          <View style={styles.qrWrapper}>
            <QRCode
              value={qrValue}
              size={120}
              color={colors.primary[700]}
              backgroundColor="#FFFFFF"
            />
          </View>
          <Text style={styles.qrPrompt}>
            Scan to verify authentic statewide KPA membership
          </Text>
        </View>

        <View style={styles.cardFooter}>
          <Text style={styles.footerNote}>
            Valid Statewide across all 31 Districts of Karnataka • Govt Reg. No. 42/1986
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
    overflow: 'hidden',
  },
  photoImage: {
    width: '100%',
    height: '100%',
    borderRadius: 7,
  },
  photoText: {
    color: colors.gold[400],
    fontSize: 16,
    fontWeight: '900',
    letterSpacing: 1,
  },
  photoSubText: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 9,
    fontWeight: '700',
    marginTop: 2,
    letterSpacing: 1,
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
  badgeContainer: {
    marginTop: 2,
    marginBottom: 6,
  },
  statusActive: {
    color: '#4ade80',
    fontSize: 11,
    fontWeight: '800',
  },
  statusPending: {
    color: '#fbbf24',
    fontSize: 11,
    fontWeight: '800',
  },
  qrContainer: {
    alignItems: 'center',
    paddingVertical: 14,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.15)',
  },
  qrWrapper: {
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  qrPrompt: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 8,
    textAlign: 'center',
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
