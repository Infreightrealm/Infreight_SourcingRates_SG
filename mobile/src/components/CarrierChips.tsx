/**
 * Carrier multi-select chips (mobile take on the web CarrierMultiSelect).
 * "All Carriers" is mutually exclusive with individual picks; empty falls
 * back to "ALL".
 */
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { CARRIERS } from '@/constants/api';
import { brandGradient, carrierColors, palette } from '@/theme/colors';

interface Props {
  selected: string[];
  onChange: (next: string[]) => void;
}

const OPTIONS = [{ code: 'ALL', name: 'All Carriers' }, ...CARRIERS] as const;

export default function CarrierChips({ selected, onChange }: Props) {
  const allSelected = selected.includes('ALL');
  const isSelected = (code: string) =>
    code === 'ALL' ? allSelected : selected.includes(code);

  const toggle = (code: string) => {
    if (code === 'ALL') {
      onChange(['ALL']);
      return;
    }
    let next = selected.filter((c) => c !== 'ALL');
    next = next.includes(code)
      ? next.filter((c) => c !== code)
      : [...next, code];
    onChange(next.length === 0 ? ['ALL'] : next);
  };

  return (
    <View style={styles.wrap}>
      {OPTIONS.map((o) => {
        const sel = isSelected(o.code);
        const accent = carrierColors[o.code];
        if (sel) {
          return (
            <Pressable key={o.code} onPress={() => toggle(o.code)}>
              <LinearGradient
                colors={brandGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={[styles.chip, styles.chipSelected]}
              >
                <Text style={styles.check}>{'✓'}</Text>
                <Text style={styles.chipTextSelected}>{o.name}</Text>
              </LinearGradient>
            </Pressable>
          );
        }
        return (
          <Pressable
            key={o.code}
            onPress={() => toggle(o.code)}
            style={({ pressed }) => [styles.chip, pressed && styles.pressed]}
          >
            {accent ? <View style={[styles.dot, { backgroundColor: accent }]} /> : null}
            <Text style={styles.chipText}>{o.name}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
    paddingHorizontal: 14,
    height: 34,
    borderRadius: 17,
    backgroundColor: palette.inputBg,
    borderWidth: 1,
    borderColor: palette.border,
  },
  chipSelected: { borderColor: 'transparent' },
  pressed: { opacity: 0.7 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  check: { color: '#fff', fontSize: 12, fontWeight: '800' },
  chipText: { color: palette.textSecondary, fontSize: 13, fontWeight: '500' },
  chipTextSelected: { color: '#fff', fontSize: 13, fontWeight: '600' },
});
