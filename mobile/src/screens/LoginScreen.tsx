/**
 * Login screen — name-only auth matching the web LoginModal.
 * Premium dark aesthetic: brand gradient logo + CTA, blue/purple accents.
 */
import { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';

import { brandGradient, palette } from '@/theme/colors';
import { loginUser } from '@/services/api';
import { useAuthStore } from '@/store/authStore';

export default function LoginScreen() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);

  const canSubmit = name.trim().length > 0 && !loading;

  const handleSubmit = async () => {
    const trimmed = name.trim();
    if (!trimmed || loading) return;
    setLoading(true);
    try {
      const user = await loginUser(trimmed);
      await login({ id: user.id, name: user.name });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong';
      Alert.alert('Login failed', message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.root}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.flex}
      >
        <View style={styles.center}>
          <LinearGradient
            colors={brandGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.logo}
          >
            <View style={styles.glyphHead} />
            <View style={styles.glyphBody} />
          </LinearGradient>

          <Text style={styles.title}>Welcome to Infreight</Text>
          <Text style={styles.subtitle}>Enter your name to start sourcing rates.</Text>

          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="e.g. Brian"
            placeholderTextColor={palette.textMuted}
            autoFocus
            autoCapitalize="words"
            autoCorrect={false}
            returnKeyType="go"
            onSubmitEditing={handleSubmit}
            editable={!loading}
            style={styles.input}
          />

          <Pressable
            onPress={handleSubmit}
            disabled={!canSubmit}
            style={({ pressed }) => [
              styles.btnWrap,
              !canSubmit && styles.btnDisabled,
              pressed && canSubmit && styles.btnPressed,
            ]}
          >
            <LinearGradient
              colors={brandGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.btn}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Text style={styles.btnText}>Start Sourcing</Text>
                  <Text style={styles.btnArrow}>{'→'}</Text>
                </>
              )}
            </LinearGradient>
          </Pressable>
        </View>

        <Text style={styles.footer}>Infreight Logistics{'  ·  '}Internal Tool</Text>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: palette.bg },
  flex: { flex: 1 },
  center: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 28,
  },
  logo: {
    width: 78,
    height: 78,
    borderRadius: 22,
    alignSelf: 'center',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingTop: 16,
    overflow: 'hidden',
    marginBottom: 28,
    shadowColor: palette.blue,
    shadowOpacity: 0.45,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: 8 },
    elevation: 12,
  },
  glyphHead: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#fff',
    marginBottom: 4,
  },
  glyphBody: {
    width: 44,
    height: 26,
    borderTopLeftRadius: 22,
    borderTopRightRadius: 22,
    backgroundColor: '#fff',
  },
  title: {
    color: palette.white,
    fontSize: 24,
    fontWeight: '800',
    textAlign: 'center',
    letterSpacing: -0.3,
  },
  subtitle: {
    color: palette.textSecondary,
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 28,
  },
  input: {
    height: 54,
    borderRadius: 15,
    backgroundColor: palette.inputBg,
    borderWidth: 1.5,
    borderColor: palette.borderHi,
    color: palette.white,
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  btnWrap: {
    marginTop: 16,
    borderRadius: 15,
    overflow: 'hidden',
    shadowColor: palette.blue,
    shadowOpacity: 0.35,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 8 },
    elevation: 8,
  },
  btnDisabled: { opacity: 0.5 },
  btnPressed: { opacity: 0.9, transform: [{ scale: 0.99 }] },
  btn: {
    height: 54,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  btnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  btnArrow: { color: '#fff', fontSize: 20, fontWeight: '700' },
  footer: {
    color: palette.textMuted,
    fontSize: 12,
    textAlign: 'center',
    paddingBottom: 16,
  },
});
