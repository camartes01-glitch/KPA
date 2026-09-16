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
import { api } from '../services/api'

interface NotificationItem {
  id: string
  title: string
  body: string
  is_read: boolean
  sent_at: string
  type: string
}

export default function NotificationsScreen() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications?lang=en')
      if (res.data?.data) {
        setNotifications(res.data.data)
      }
    } catch {
      // Handle offline
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
  }, [])

  const onRefresh = () => {
    setRefreshing(true)
    fetchNotifications()
  }

  const handleMarkRead = async (id: string) => {
    try {
      await api.post(`/notifications/${id}/read`)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
    } catch {
      // Ignore
    }
  }

  const handleNotificationPress = (n: NotificationItem) => {
    handleMarkRead(n.id)
    const formatted = new Date(n.sent_at).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
    Alert.alert(n.title, `${n.body}\n\nReceived: ${formatted}`)
  }

  const handleMarkAllRead = async () => {
    const unread = notifications.filter((n) => !n.is_read)
    for (const item of unread) {
      handleMarkRead(item.id)
    }
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary[700]} />}
    >
      <View style={styles.headerRow}>
        <View>
          <Text style={styles.heading}>Notifications</Text>
          <Text style={styles.subheading}>Welfare announcements, payment vouchers, and alerts</Text>
        </View>
        {unreadCount > 0 && (
          <TouchableOpacity
            style={styles.markAllButton}
            onPress={handleMarkAllRead}
            activeOpacity={0.7}
          >
            <Text style={styles.markAllText}>Mark all read</Text>
          </TouchableOpacity>
        )}
      </View>

      {loading && notifications.length === 0 ? (
        <ActivityIndicator size="small" color={colors.primary[700]} style={{ marginVertical: 30 }} />
      ) : notifications.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyTitle}>No Notifications</Text>
          <Text style={styles.emptyDesc}>You are up to date on all association events and announcements.</Text>
        </View>
      ) : (
        notifications.map((n) => (
          <TouchableOpacity
            key={n.id}
            style={[styles.card, !n.is_read && styles.cardUnread]}
            onPress={() => handleNotificationPress(n)}
            activeOpacity={0.8}
          >
            <View style={styles.cardHeader}>
              <Text style={[styles.title, !n.is_read && styles.titleUnread]}>{n.title}</Text>
              {!n.is_read && <View style={styles.unreadDot} />}
            </View>

            <Text style={styles.body}>{n.body}</Text>

            <Text style={styles.time}>
              {new Date(n.sent_at).toLocaleString('en-IN', {
                day: '2-digit',
                month: 'short',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
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
  },
  markAllButton: {
    backgroundColor: colors.primary[50],
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.primary[100],
  },
  markAllText: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.primary[700],
  },
  emptyCard: {
    backgroundColor: colors.neutral.white,
    borderRadius: 16,
    padding: 30,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.neutral.border,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.neutral.text,
    marginBottom: 6,
  },
  emptyDesc: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    textAlign: 'center',
  },
  card: {
    backgroundColor: colors.neutral.white,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.neutral.border,
    marginBottom: 12,
  },
  cardUnread: {
    borderColor: colors.primary[700],
    backgroundColor: '#f8fafc',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  title: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.neutral.text,
    flex: 1,
  },
  titleUnread: {
    fontWeight: '800',
    color: colors.primary[700],
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary[700],
    marginLeft: 8,
  },
  body: {
    fontSize: 13,
    color: colors.neutral.textSecondary,
    lineHeight: 18,
    marginBottom: 8,
  },
  time: {
    fontSize: 11,
    color: colors.neutral.textMuted,
  },
})
