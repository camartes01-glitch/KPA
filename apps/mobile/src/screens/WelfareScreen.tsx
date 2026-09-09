import React from 'react'
import { View, Text, StyleSheet, ScrollView } from 'react-native'
import { colors } from '../theme/colors'

export default function WelfareScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Welfare Events & Relief</Text>
      <Text style={styles.subheading}>
        Mutual bereavement benefit fund for registered photographer families
      </Text>

      <View style={styles.noticeCard}>
        <Text style={styles.noticeTitle}>Automatic ₹10 Mutual Fund</Text>
        <Text style={styles.noticeBody}>
          Upon verified demise of an association member, an automated ₹10 relief contribution is debited through AutoPay/UPI to support the bereaved family.
        </Text>
      </View>

      <View style={styles.emptyCard}>
        <Text style={styles.emptyTitle}>No Active Emergency Cases</Text>
        <Text style={styles.emptyDesc}>
          All mutual welfare claims have been settled. You will receive an instant notification when a new welfare relief event is approved by the State Committee.
        </Text>
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
  emptyCard: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 8,
  },
  emptyDesc: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    textAlign: 'center',
    lineHeight: 18,
  },
})
