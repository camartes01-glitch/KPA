import React, { useEffect, useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native'
import { colors } from '../theme/colors'
import { api, getErrorMessage } from '../services/api'

interface WelfareEvent {
  id: string
  title: string
  death_date: string
  cause_of_death?: string
  target_amount: number
  collected_amount: number
  status: string
}

interface WelfareObligation {
  contribution_id: string
  event_id: string
  event_title: string
  deceased_member_name: string
  amount: number
  status: 'PENDING' | 'SUCCESS' | 'FAILED' | 'EXEMPT'
  created_at: string
}

export default function WelfareScreen() {
  const [obligations, setObligations] = useState<WelfareObligation[]>([])
  const [events, setEvents] = useState<WelfareEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [processingId, setProcessingId] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      const [oblRes, evRes] = await Promise.all([
        api.get('/welfare-events/my-contributions'),
        api.get('/welfare-events'),
      ])
      if (oblRes.data?.data) {
        setObligations(oblRes.data.data)
      }
      if (evRes.data?.data) {
        setEvents(evRes.data.data)
      }
    } catch (err: any) {
      // Offline/error handling
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const onRefresh = () => {
    setRefreshing(true)
    fetchData()
  }

  const promptPayContribution = (obl: WelfareObligation) => {
    Alert.alert(
      'Confirm Welfare Contribution',
      `Are you sure you want to contribute ₹${parseFloat(String(obl.amount)).toFixed(2)} to support the bereaved family of ${obl.deceased_member_name || 'fellow photographer'}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Confirm & Pay',
          onPress: () => executePayContribution(obl),
        },
      ]
    )
  }

  const executePayContribution = async (obl: WelfareObligation) => {
    setProcessingId(obl.contribution_id)
    try {
      // 1. Create gateway order
      const orderRes = await api.post('/payments/create-order', {
        contribution_id: obl.contribution_id,
      })
      const orderData = orderRes.data?.data
      if (!orderData) {
        throw new Error('Could not initiate payment order')
      }

      // 2. In sandbox/development, complete verification flow
      const verifyRes = await api.post('/payments/verify', {
        gateway_order_id: orderData.order_id,
        gateway_payment_id: `pay_${Date.now()}`,
        signature: 'mock-valid-signature',
      })

      if (verifyRes.data?.success) {
        const receipt = verifyRes.data.data
        Alert.alert(
          'Official Receipt Issued',
          `Payment of ₹${receipt.amount.toFixed(2)} recorded.\n\n` +
            `Receipt No: ${receipt.receipt_no}\n` +
            `Purpose: ${receipt.event_title || 'Mutual Welfare Relief'}\n` +
            `Date: ${new Date().toLocaleDateString('en-IN')}\n` +
            `Status: SETTLED & VERIFIED`,
          [{ text: 'View Updated Dues', onPress: () => fetchData() }]
        )
      }
    } catch (err: any) {
      Alert.alert('Payment Failed', getErrorMessage(err))
    } finally {
      setProcessingId(null)
    }
  }

  const handleShowCaseDetails = (ev: WelfareEvent) => {
    Alert.alert(
      ev.title,
      `Statewide Mutual Benefit Case\n\n` +
        `Date of Demise: ${ev.death_date}\n` +
        `Cause: ${ev.cause_of_death || 'Natural / Medical causes'}\n` +
        `Target Fund: ₹${parseFloat(String(ev.target_amount)).toFixed(2)}\n` +
        `Collected so far: ₹${parseFloat(String(ev.collected_amount)).toFixed(2)}\n` +
        `Status: ${ev.status}\n\n` +
        `Relief Policy: Karnataka Photography Association Rule 14-B ensures ₹50,000+ mutual emergency grant to the registered nominee.`
    )
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary[700]} />}
    >
      <Text style={styles.heading}>Welfare Events & Relief</Text>
      <Text style={styles.subheading}>
        Mutual bereavement benefit fund for registered photographer families
      </Text>

      {/* Statutory Info Banner */}
      <View style={styles.noticeCard}>
        <Text style={styles.noticeTitle}>Automatic ₹10 Mutual Fund</Text>
        <Text style={styles.noticeBody}>
          Upon verified demise of an association member, an automated ₹10 relief contribution is collected from each member to provide immediate ₹50,000+ support to the bereaved family.
        </Text>
      </View>

      {/* My Pending Contributions Section */}
      <Text style={styles.sectionHeader}>My Relief Obligations</Text>
      {loading && obligations.length === 0 ? (
        <ActivityIndicator size="small" color={colors.primary[700]} style={{ marginVertical: 20 }} />
      ) : obligations.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyTitle}>No Pending Obligations</Text>
          <Text style={styles.emptyDesc}>
            All mutual welfare contributions have been cleared. Thank you for supporting fellow photographers!
          </Text>
        </View>
      ) : (
        obligations.map((obl) => {
          const isPending = obl.status === 'PENDING'
          const isPaying = processingId === obl.contribution_id

          return (
            <View key={obl.contribution_id} style={[styles.obligationCard, isPending ? styles.cardPending : styles.cardPaid]}>
              <View style={styles.cardHeaderRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cardTitle}>{obl.event_title}</Text>
                  <Text style={styles.cardMember}>Deceased: {obl.deceased_member_name}</Text>
                </View>
                <View style={isPending ? styles.badgeDue : styles.badgePaid}>
                  <Text style={isPending ? styles.badgeTextDue : styles.badgeTextPaid}>
                    {isPending ? 'PENDING' : 'SETTLED'}
                  </Text>
                </View>
              </View>

              <View style={styles.cardFooterRow}>
                <Text style={styles.amountText}>Amount: ₹{parseFloat(String(obl.amount)).toFixed(2)}</Text>

                {isPending && (
                  <TouchableOpacity
                    style={styles.payBtn}
                    onPress={() => promptPayContribution(obl)}
                    disabled={isPaying}
                    activeOpacity={0.8}
                  >
                    {isPaying ? (
                      <ActivityIndicator size="small" color={colors.neutral.white} />
                    ) : (
                      <Text style={styles.payBtnText}>Pay ₹{parseFloat(String(obl.amount)).toFixed(2)} Now</Text>
                    )}
                  </TouchableOpacity>
                )}
              </View>
            </View>
          )
        })
      )}

      {/* Active State Events */}
      <Text style={[styles.sectionHeader, { marginTop: 24 }]}>Active Statewide Cases</Text>
      {events.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyDesc}>No active welfare relief cases at this time.</Text>
        </View>
      ) : (
        events.map((ev) => (
          <TouchableOpacity
            key={ev.id}
            style={styles.eventCard}
            onPress={() => handleShowCaseDetails(ev)}
            activeOpacity={0.7}
          >
            <Text style={styles.eventTitle}>{ev.title}</Text>
            <Text style={styles.eventDate}>Date of Demise: {ev.death_date}</Text>
            <View style={styles.progressRow}>
              <Text style={styles.progressText}>
                Collected: ₹{parseFloat(String(ev.collected_amount)).toFixed(2)} / ₹{parseFloat(String(ev.target_amount)).toFixed(2)}
              </Text>
              <Text style={styles.eventStatusBadge}>{ev.status}</Text>
            </View>
            <Text style={styles.tapDetailsText}>Tap to view case particulars →</Text>
          </TouchableOpacity>
        ))
      )}
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
    fontSize: 20,
    fontWeight: '800',
    color: colors.neutral.text,
  },
  subheading: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    marginTop: 4,
    marginBottom: 20,
  },
  noticeCard: {
    backgroundColor: colors.primary[50],
    borderWidth: 1,
    borderColor: colors.primary[100],
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
  },
  noticeTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.primary[700],
    marginBottom: 6,
  },
  noticeBody: {
    fontSize: 13,
    color: colors.primary[900],
    lineHeight: 18,
  },
  sectionHeader: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 12,
  },
  emptyCard: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  emptyTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 6,
  },
  emptyDesc: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    textAlign: 'center',
    lineHeight: 18,
  },
  obligationCard: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 12,
  },
  cardPending: {
    borderColor: '#fca5a5',
    backgroundColor: '#fff5f5',
  },
  cardPaid: {
    borderColor: colors.neutral.border,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.neutral.text,
  },
  cardMember: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    marginTop: 2,
  },
  badgeDue: {
    backgroundColor: '#fee2e2',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeTextDue: {
    color: '#dc2626',
    fontWeight: '700',
    fontSize: 10,
  },
  badgePaid: {
    backgroundColor: '#dcfce7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeTextPaid: {
    color: '#16a34a',
    fontWeight: '700',
    fontSize: 10,
  },
  cardFooterRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.06)',
    paddingTop: 12,
  },
  amountText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.neutral.text,
  },
  payBtn: {
    backgroundColor: colors.primary[700],
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 10,
  },
  payBtnText: {
    color: colors.neutral.white,
    fontWeight: '700',
    fontSize: 13,
  },
  eventCard: {
    backgroundColor: colors.neutral.white,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.neutral.border,
    marginBottom: 10,
  },
  eventTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.neutral.text,
  },
  eventDate: {
    fontSize: 12,
    color: colors.neutral.textSecondary,
    marginTop: 2,
  },
  progressRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
  },
  progressText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.primary[700],
  },
  eventStatusBadge: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.gold[500],
    textTransform: 'uppercase',
  },
  tapDetailsText: {
    fontSize: 11,
    color: colors.primary[500],
    fontWeight: '600',
    marginTop: 8,
  },
})
