/**
 * SettingsScreen — the second tab. Shows the signed-in user, the backend the
 * app is pointed at, and a sign-out action.
 */
import { useEffect, useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';

import { API_URL } from '@/constants/api';
import { healthCheck } from '@/services/api';
import { brandGradient, palette } from '@/theme/colors';
import { useAuthStore } from '@/store/authStore';

export default function SettingsScreen() {
  const insets = useSafeAreaInsets();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking');
  const [mockMode, setMockMode] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    healthCheck()
      .then((h) => {
        if (!active) return;
        setHealth('online');
        setMockMode(h.mock_mode);
      })
      .catch(() => active && setHealth('offline'));
    return () => {
      active = false;
    };
  }, []);

  const confirmLogout = () => {
    Alert.alert('Sign out', 'Sign out of Infreight?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign out', style: 'destructive', onPress: () => logout() },
    ]);
  };

  const healthColor =
    health === 'online' ? palette.emerald : health === 'offline' ? palette.red : palette.textMuted;
  const healthLabel =
    health === 'online' ? 'Online' : health === 'offline' ? 'Unreachable' : 'Checking…';

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={[styles.content, { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 120 }]}
    >
      <Text style={styles.title}>Settings</Text>

      <View style={styles.card}>
        <LinearGradient colors={brandGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.avatar}>
          <Text style={styles.avatarText}>{(user?.name?.[0] ?? '?').toUpperCase()}</Text>
        </LinearGradient>
        <View style={styles.userText}>
          <Text style={styles.userName}>{user?.name ?? 'Unknown user'}</Text>
          <Text style={styles.userSub}>Signed in</Text>
        </View>
      </View>

      <Text style={styles.sectionLabel}>BACKEND</Text>
      <View style={styles.infoCard}>
        <InfoRow label="API URL" value={API_URL} />
        <View style={styles.divider} />
        <View style={styles.statusRow}>
          <Text style={styles.infoLabel}>Status</Text>
          <View style={styles.statusValue}>
            <View style={[styles.statusDot, { backgroundColor: healthColor }]} />
            <Text style={[styles.infoValue, { color: healthColor }]}>{healthLabel}</Text>
          </View>
        </View>
        {mockMode !== null ? (
          <>
            <View style={styles.divider} />
            <InfoRow label="Mode" value={mockMode ? 'Mock data' : 'Live carriers'} />
          </>
        ) : null}
      </View>

      <Pressable onPress={confirmLogout} style={({ pressed }) => [styles.logoutBtn, pressed && { opacity: 0.7 }]}>
        <Text style={styles.logoutText}>Sign out</Text>
      </Pressable>
    </ScrollView>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue} numberOfLines={1}>
        {value}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: palette.bg },
  content: { paddingHorizontal: 20 },
  title: { color: palette.white, fontSize: 22, fontWeight: '800', marginBottom: 20, letterSpacing: -0.3 },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    backgroundColor: palette.card,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    padding: 16,
    marginBottom: 24,
  },
  avatar: { width: 52, height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontSize: 22, fontWeight: '800' },
  userText: { flex: 1 },
  userName: { color: palette.white, fontSize: 17, fontWeight: '700' },
  userSub: { color: palette.textMuted, fontSize: 12.5, marginTop: 2 },
  sectionLabel: { color: palette.textMuted, fontSize: 11, fontWeight: '700', letterSpacing: 1.2, marginBottom: 10 },
  infoCard: { backgroundColor: palette.card, borderRadius: 18, borderWidth: 1, borderColor: palette.border, paddingHorizontal: 16 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 14, gap: 16 },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 14 },
  statusValue: { flexDirection: 'row', alignItems: 'center', gap: 7 },
  statusDot: { width: 8, height: 8, borderRadius: 4 },
  infoLabel: { color: palette.textSecondary, fontSize: 13.5 },
  infoValue: { color: palette.white, fontSize: 13.5, fontWeight: '600', flexShrink: 1, textAlign: 'right' },
  divider: { height: 1, backgroundColor: palette.border },
  logoutBtn: {
    marginTop: 28,
    height: 52,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(248,113,113,0.10)',
    borderWidth: 1,
    borderColor: 'rgba(248,113,113,0.25)',
  },
  logoutText: { color: palette.red, fontSize: 15, fontWeight: '700' },
});
