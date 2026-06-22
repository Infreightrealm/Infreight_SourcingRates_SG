/**
 * SearchScreen — the primary tab. Holds the rate-search form and, once a search
 * is running, swaps to the live results list (per-carrier QuoteCards), mirroring
 * the web app's single-page form/results flow.
 */
import { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';

import CarrierChips from '@/components/CarrierChips';
import PortField from '@/components/PortField';
import QuoteCard from '@/components/QuoteCard';
import { CONTAINER_TYPES, statusStyle } from '@/constants/api';
import { useRateSearch } from '@/hooks/useRateSearch';
import { brandGradient, palette } from '@/theme/colors';
import { useAuthStore } from '@/store/authStore';
import type { RateSearchRequest } from '@/types/api';

const SEARCH_WINDOWS = [7, 14, 21, 30];

export default function SearchScreen() {
  const insets = useSafeAreaInsets();
  const userName = useAuthStore((s) => s.user?.name);
  const search = useRateSearch();

  // Form state
  const [carriers, setCarriers] = useState<string[]>(['ALL']);
  const [origin, setOrigin] = useState('Singapore');
  const [destination, setDestination] = useState('Hamburg');
  const [containerType, setContainerType] = useState('DRY 40H');
  const [containerQty, setContainerQty] = useState('1');
  const [weight, setWeight] = useState('20000');
  const [commodity, setCommodity] = useState('Furniture');
  const [departureDate, setDepartureDate] = useState('tomorrow');
  const [searchWindow, setSearchWindow] = useState(14);

  const submit = () => {
    if (carriers.length === 0) return;
    if (!origin.trim() || !destination.trim()) {
      Alert.alert('Missing route', 'Please enter both an origin and a destination.');
      return;
    }
    const request: RateSearchRequest = {
      carriers,
      origin: origin.trim(),
      destination: destination.trim(),
      service_term: 'CY/CY',
      container_type: containerType,
      container_quantity: Math.max(1, parseInt(containerQty, 10) || 1),
      weight_per_container_kg: Math.max(1, parseFloat(weight) || 20000),
      commodity: commodity.trim() || 'General Cargo',
      departure_date: departureDate.trim() || 'tomorrow',
      search_window_days: searchWindow,
      user_name: userName,
    };
    search.start(request);
  };

  const showResults = !!search.searchId;

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={[
        styles.content,
        { paddingTop: insets.top + 12, paddingBottom: insets.bottom + 120 },
      ]}
      keyboardShouldPersistTaps="handled"
    >
      <View style={styles.header}>
        <LinearGradient colors={brandGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.logo}>
          <Text style={styles.logoText}>IF</Text>
        </LinearGradient>
        <View style={styles.headerText}>
          <Text style={styles.title}>{showResults ? 'Rate Results' : 'New Rate Search'}</Text>
          <Text style={styles.subtitle}>
            {showResults ? `${origin} → ${destination}` : 'Compare ocean freight quotes'}
          </Text>
        </View>
      </View>

      {showResults ? (
        <ResultsSection search={search} onNewSearch={search.reset} />
      ) : (
        <View style={styles.form}>
          <Text style={styles.sectionLabel}>CARRIERS</Text>
          <CarrierChips selected={carriers} onChange={setCarriers} />

          <View style={styles.routeRow}>
            <PortField label="ORIGIN" value={origin} onChange={setOrigin} placeholder="e.g. Singapore" />
            <PortField label="DESTINATION" value={destination} onChange={setDestination} placeholder="e.g. Hamburg" />
          </View>

          <Text style={styles.sectionLabel}>CONTAINER TYPE</Text>
          <View style={styles.chipRow}>
            {CONTAINER_TYPES.map((t) => {
              const sel = t === containerType;
              return (
                <Pressable key={t} onPress={() => setContainerType(t)}>
                  {sel ? (
                    <LinearGradient colors={brandGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.typeChip}>
                      <Text style={styles.typeChipTextSel}>{t}</Text>
                    </LinearGradient>
                  ) : (
                    <View style={[styles.typeChip, styles.typeChipIdle]}>
                      <Text style={styles.typeChipText}>{t}</Text>
                    </View>
                  )}
                </Pressable>
              );
            })}
          </View>

          <View style={styles.fieldRow}>
            <LabeledInput label="QUANTITY" value={containerQty} onChangeText={setContainerQty} keyboardType="number-pad" />
            <LabeledInput label="WEIGHT / CTR (KG)" value={weight} onChangeText={setWeight} keyboardType="number-pad" />
          </View>
          <View style={styles.fieldRow}>
            <LabeledInput label="COMMODITY" value={commodity} onChangeText={setCommodity} />
            <LabeledInput label="DEPARTURE" value={departureDate} onChangeText={setDepartureDate} />
          </View>

          <Text style={styles.sectionLabel}>SEARCH WINDOW</Text>
          <View style={styles.chipRow}>
            {SEARCH_WINDOWS.map((d) => {
              const sel = d === searchWindow;
              return (
                <Pressable key={d} onPress={() => setSearchWindow(d)}>
                  {sel ? (
                    <LinearGradient colors={brandGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.typeChip}>
                      <Text style={styles.typeChipTextSel}>{d} days</Text>
                    </LinearGradient>
                  ) : (
                    <View style={[styles.typeChip, styles.typeChipIdle]}>
                      <Text style={styles.typeChipText}>{d} days</Text>
                    </View>
                  )}
                </Pressable>
              );
            })}
          </View>

          <Pressable
            onPress={submit}
            disabled={search.isCreating}
            style={({ pressed }) => [styles.searchBtnWrap, pressed && { opacity: 0.9 }]}
          >
            <LinearGradient colors={brandGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={styles.searchBtn}>
              {search.isCreating ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.searchBtnText}>Search Rates</Text>
              )}
            </LinearGradient>
          </Pressable>
        </View>
      )}
    </ScrollView>
  );
}

function ResultsSection({
  search,
  onNewSearch,
}: {
  search: ReturnType<typeof useRateSearch>;
  onNewSearch: () => void;
}) {
  const overall = statusStyle(search.status ?? 'QUEUED');
  const results = search.result?.results ?? [];
  const queuePos = search.result?.queue_position;

  return (
    <View>
      <View style={styles.resultsBar}>
        <View style={[styles.badge, { backgroundColor: overall.bg }]}>
          {search.isPolling ? (
            <ActivityIndicator size="small" color={overall.color} />
          ) : (
            <View style={[styles.badgeDot, { backgroundColor: overall.color }]} />
          )}
          <Text style={[styles.badgeText, { color: overall.color }]}>{overall.label}</Text>
        </View>
        <Pressable onPress={onNewSearch} style={({ pressed }) => [styles.newBtn, pressed && { opacity: 0.7 }]}>
          <Text style={styles.newBtnText}>New Search</Text>
        </Pressable>
      </View>

      {typeof queuePos === 'number' && queuePos > 0 ? (
        <Text style={styles.queueText}>Queue position: {queuePos}</Text>
      ) : null}

      {results.length === 0 ? (
        <View style={styles.emptyState}>
          <ActivityIndicator color={palette.blue} />
          <Text style={styles.emptyText}>Dispatching carrier searches…</Text>
        </View>
      ) : (
        <View style={styles.cards}>
          {results.map((r) => (
            <QuoteCard
              key={r.carrier}
              result={r}
              onSolve={(carrier) =>
                Alert.alert(
                  'Human verification',
                  `${carrier} needs a CAPTCHA/2FA solved. The in-app verification view is coming in the next build step.`,
                )
              }
            />
          ))}
        </View>
      )}
    </View>
  );
}

function LabeledInput({
  label,
  value,
  onChangeText,
  keyboardType,
}: {
  label: string;
  value: string;
  onChangeText: (v: string) => void;
  keyboardType?: 'default' | 'number-pad';
}) {
  return (
    <View style={styles.labeledInput}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        keyboardType={keyboardType ?? 'default'}
        placeholderTextColor={palette.textMuted}
        style={styles.input}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: palette.bg },
  content: { paddingHorizontal: 20 },
  header: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 22 },
  logo: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  logoText: { color: '#fff', fontSize: 16, fontWeight: '800' },
  headerText: { flex: 1 },
  title: { color: palette.white, fontSize: 18, fontWeight: '800', letterSpacing: -0.3 },
  subtitle: { color: palette.textMuted, fontSize: 12.5, marginTop: 2 },
  form: { gap: 16 },
  sectionLabel: { color: palette.textMuted, fontSize: 11, fontWeight: '700', letterSpacing: 1.2 },
  routeRow: { flexDirection: 'row', gap: 12, zIndex: 10 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  typeChip: { paddingHorizontal: 14, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center' },
  typeChipIdle: { backgroundColor: palette.inputBg, borderWidth: 1, borderColor: palette.border },
  typeChipText: { color: palette.textSecondary, fontSize: 13, fontWeight: '500' },
  typeChipTextSel: { color: '#fff', fontSize: 13, fontWeight: '600' },
  fieldRow: { flexDirection: 'row', gap: 12 },
  labeledInput: { flex: 1 },
  fieldLabel: { color: palette.textSecondary, fontSize: 11.5, fontWeight: '600', letterSpacing: 0.3, marginBottom: 6 },
  input: {
    height: 48,
    borderRadius: 13,
    paddingHorizontal: 14,
    backgroundColor: palette.inputBg,
    borderWidth: 1,
    borderColor: palette.border,
    color: palette.white,
    fontSize: 14.5,
    fontWeight: '600',
  },
  searchBtnWrap: { marginTop: 10, borderRadius: 16, overflow: 'hidden' },
  searchBtn: { height: 56, alignItems: 'center', justifyContent: 'center' },
  searchBtnText: { color: '#fff', fontSize: 16.5, fontWeight: '700' },
  // results
  resultsBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 },
  badge: { flexDirection: 'row', alignItems: 'center', gap: 7, paddingHorizontal: 12, height: 28, borderRadius: 14 },
  badgeDot: { width: 7, height: 7, borderRadius: 3.5 },
  badgeText: { fontSize: 12.5, fontWeight: '600' },
  newBtn: { paddingHorizontal: 14, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center', backgroundColor: palette.inputBg, borderWidth: 1, borderColor: palette.border },
  newBtnText: { color: palette.white, fontSize: 13, fontWeight: '600' },
  queueText: { color: palette.textMuted, fontSize: 12, marginBottom: 12 },
  emptyState: { alignItems: 'center', gap: 12, paddingVertical: 40 },
  emptyText: { color: palette.textSecondary, fontSize: 13 },
  cards: { gap: 14 },
});
