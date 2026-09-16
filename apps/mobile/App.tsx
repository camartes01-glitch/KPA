import React, { useEffect } from 'react'
import { View, ActivityIndicator, TouchableOpacity, StyleSheet } from 'react-native'
import { StatusBar } from 'expo-status-bar'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { useAuthStore } from './src/store/authStore'
import { colors } from './src/theme/colors'

import LoginScreen from './src/screens/LoginScreen'
import HomeScreen from './src/screens/HomeScreen'
import DigitalCardScreen from './src/screens/DigitalCardScreen'
import WelfareScreen from './src/screens/WelfareScreen'
import NotificationsScreen from './src/screens/NotificationsScreen'
import ProfileScreen from './src/screens/ProfileScreen'
import SettingsScreen from './src/screens/SettingsScreen'
import { Ionicons } from '@expo/vector-icons'
import { enableScreens } from 'react-native-screens'

enableScreens()

const Stack = createNativeStackNavigator()
const Tab = createBottomTabNavigator()

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerStyle: {
          backgroundColor: colors.primary[700],
        },
        headerTintColor: colors.neutral.white,
        tabBarActiveTintColor: colors.primary[700],
        tabBarInactiveTintColor: colors.neutral.textSecondary,
        tabBarIcon: ({ color, size, focused }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'help-outline'

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline'
          } else if (route.name === 'DigitalCard') {
            iconName = focused ? 'id-card' : 'id-card-outline'
          } else if (route.name === 'Welfare') {
            iconName = focused ? 'heart' : 'heart-outline'
          } else if (route.name === 'Notifications') {
            iconName = focused ? 'notifications' : 'notifications-outline'
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline'
          }

          return <Ionicons name={iconName} size={size} color={color} />
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={({ navigation }: any) => ({
          title: 'Home',
          headerRight: () => (
            <TouchableOpacity
              onPress={() => navigation.navigate('Settings')}
              style={{ marginRight: 16, padding: 4 }}
              activeOpacity={0.7}
            >
              <Ionicons name="settings-outline" size={22} color={colors.neutral.white} />
            </TouchableOpacity>
          ),
        })}
      />
      <Tab.Screen
        name="DigitalCard"
        component={DigitalCardScreen}
        options={{ title: 'ID Card' }}
      />
      <Tab.Screen
        name="Welfare"
        component={WelfareScreen}
        options={{ title: 'Welfare' }}
      />
      <Tab.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{ title: 'Alerts' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={({ navigation }: any) => ({
          title: 'Profile',
          headerRight: () => (
            <TouchableOpacity
              onPress={() => navigation.navigate('Settings')}
              style={{ marginRight: 16, padding: 4 }}
              activeOpacity={0.7}
            >
              <Ionicons name="settings-outline" size={22} color={colors.neutral.white} />
            </TouchableOpacity>
          ),
        })}
      />
    </Tab.Navigator>
  )
}

export default function App() {
  const { isAuthenticated, isHydrated, hydrate } = useAuthStore()

  useEffect(() => {
    hydrate()
  }, [])

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      {!isHydrated ? (
        <View style={appStyles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.gold[400]} />
        </View>
      ) : (
        <NavigationContainer>
          <Stack.Navigator screenOptions={{ headerShown: false }}>
            {!isAuthenticated ? (
              <Stack.Screen name="Login" component={LoginScreen} />
            ) : (
              <Stack.Group>
                <Stack.Screen name="Main" component={MainTabs} />
                <Stack.Screen
                  name="Settings"
                  component={SettingsScreen}
                  options={({ navigation }) => ({
                    headerShown: true,
                    title: 'Settings',
                    headerStyle: { backgroundColor: colors.primary[700] },
                    headerTintColor: colors.neutral.white,
                    headerLeft: () => (
                      <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        style={{ paddingHorizontal: 4, paddingVertical: 4, marginRight: 8 }}
                        activeOpacity={0.7}
                        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                      >
                        <Ionicons name="arrow-back" size={24} color={colors.neutral.white} />
                      </TouchableOpacity>
                    ),
                  })}
                />
              </Stack.Group>
            )}
          </Stack.Navigator>
        </NavigationContainer>
      )}
    </SafeAreaProvider>
  )
}

const appStyles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: colors.primary[700],
    justifyContent: 'center',
    alignItems: 'center',
  },
})

