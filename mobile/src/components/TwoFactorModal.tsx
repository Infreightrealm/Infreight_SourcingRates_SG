/**
 * TwoFactorModal — in-app human verification.
 *
 * Loads the carrier's noVNC viewer (served by the backend) in a WebView so the
 * user can solve a CAPTCHA / 2FA without leaving the app. Carrier paths come
 * from /api/vnc-status; the viewer itself lives on the same backend URL.
 */
import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Modal,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';

import { API_URL, VNC_CARRIER_CODE } from '@/constants/api';
import { getVncStatus } from '@/services/api';
import { CARRIERS } from '@/constants/api';
import { palette } from '@/theme/colors';

interface Props {
  /** Rate-search carrier code (e.g. "MAERSK"), or null when closed. */
  carrierCode: string | null;
  onClose: () => void;
}

type LoadState =
  | { phase: 'loading' }
  | { phase: 'unavailable'; message: string }
  | { phase: 'ready'; url: string };

function carrierName(code: string): string {
  return CARRIERS.find((c) => c.code === code)?.name ?? code;
}

export default function TwoFactorModal({ carrierCode, onClose }: Props) {
  const open = !!carrierCode;
  const [state, setState] = useState<LoadState>({ phase: 'loading' });

  useEffect(() => {
    if (!carrierCode) return;
    let active = true;
    setState({ phase: 'loading' });

    getVncStatus()
      .then((status) => {
        if (!active) return;
        if (!status.available) {
          setState({
            phase: 'unavailable',
            message:
              status.message ||
              'The live verification viewer is only available when the backend runs in production mode.',
          });
          return;
        }
        const vncCode = VNC_CARRIER_CODE[carrierCode] ?? carrierCode.toLowerCase();
        const carrier = status.carriers.find((c) => c.code === vncCode);
        if (!carrier) {
          setState({
            phase: 'unavailable',
            message: `No verification viewer is available for ${carrierName(carrierCode)}.`,
          });
          return;
        }
        const path = carrier.path.startsWith('/') ? carrier.path : `/${carrier.path}`;
        setState({ phase: 'ready', url: `${API_URL}${path}` });
      })
      .catch(() => {
        if (active) {
          setState({
            phase: 'unavailable',
            message: 'Could not reach the backend to start verification.',
          });
        }
      });

    return () => {
      active = false;
    };
  }, [carrierCode]);

  return (
    <Modal visible={open} animationType="slide" onRequestClose={onClose} presentationStyle="fullScreen">
      <SafeAreaView style={styles.root} edges={['top', 'bottom']}>
        <View style={styles.header}>
          <View style={styles.headerText}>
            <Text style={styles.title}>Human Verification</Text>
            <Text style={styles.subtitle}>
              {carrierCode ? carrierName(carrierCode) : ''} · solve the CAPTCHA / 2FA
            </Text>
          </View>
          <Pressable onPress={onClose} hitSlop={10} style={({ pressed }) => [styles.close, pressed && { opacity: 0.6 }]}>
            <Text style={styles.closeText}>Done</Text>
          </Pressable>
        </View>

        <View style={styles.body}>
          {state.phase === 'loading' ? (
            <View style={styles.center}>
              <ActivityIndicator color={palette.blue} />
              <Text style={styles.centerText}>Connecting to verification viewer…</Text>
            </View>
          ) : state.phase === 'unavailable' ? (
            <View style={styles.center}>
              <Text style={styles.unavailableTitle}>Viewer unavailable</Text>
              <Text style={styles.centerText}>{state.message}</Text>
            </View>
          ) : (
            <WebView
              source={{ uri: state.url }}
              style={styles.webview}
              originWhitelist={['*']}
              javaScriptEnabled
              domStorageEnabled
              scalesPageToFit
              startInLoadingState
              renderLoading={() => (
                <View style={styles.center}>
                  <ActivityIndicator color={palette.blue} />
                </View>
              )}
            />
          )}
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerHint}>
            When the carrier portal continues past the challenge, tap Done — results will keep updating.
          </Text>
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: palette.bg },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: palette.border,
  },
  headerText: { flex: 1 },
  title: { color: palette.white, fontSize: 17, fontWeight: '800' },
  subtitle: { color: palette.textMuted, fontSize: 12.5, marginTop: 2 },
  close: { paddingHorizontal: 14, height: 34, borderRadius: 17, alignItems: 'center', justifyContent: 'center', backgroundColor: palette.inputBg, borderWidth: 1, borderColor: palette.border },
  closeText: { color: palette.white, fontSize: 14, fontWeight: '700' },
  body: { flex: 1 },
  webview: { flex: 1, backgroundColor: palette.bg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12, padding: 32 },
  centerText: { color: palette.textSecondary, fontSize: 13.5, textAlign: 'center', lineHeight: 20 },
  unavailableTitle: { color: palette.white, fontSize: 16, fontWeight: '700' },
  footer: { paddingHorizontal: 20, paddingVertical: 12, borderTopWidth: 1, borderTopColor: palette.border },
  footerHint: { color: palette.textMuted, fontSize: 12, textAlign: 'center', lineHeight: 17 },
});
