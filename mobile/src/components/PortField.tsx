/**
 * Port input with debounced autocomplete (mobile take on PortAutocomplete).
 * Suggestions render in-flow below the field (no absolute overlay) so it plays
 * nicely inside a ScrollView and keeps touch targets large.
 */
import { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { getPortSuggestions } from '@/services/api';
import type { PortSuggestion } from '@/types/api';
import { palette } from '@/theme/colors';

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function PortField({ label, value, onChange, placeholder }: Props) {
  const [suggestions, setSuggestions] = useState<PortSuggestion[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const justSelected = useRef(false);

  useEffect(() => {
    if (justSelected.current) {
      justSelected.current = false;
      return;
    }
    if (value.trim().length < 2) {
      setSuggestions([]);
      setOpen(false);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const results = await getPortSuggestions(value.trim());
        setSuggestions(results);
        setOpen(results.length > 0);
      } catch {
        /* ignore transient lookup errors */
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [value]);

  const select = (port: PortSuggestion) => {
    justSelected.current = true;
    onChange(port.code ? `${port.name} (${port.code})` : port.name);
    setSuggestions([]);
    setOpen(false);
  };

  return (
    <View style={styles.wrap}>
      <Text style={styles.label}>{label}</Text>
      <View>
        <TextInput
          value={value}
          onChangeText={onChange}
          placeholder={placeholder}
          placeholderTextColor={palette.textMuted}
          autoCapitalize="words"
          autoCorrect={false}
          style={styles.input}
        />
        {loading ? (
          <ActivityIndicator size="small" color={palette.blue} style={styles.spinner} />
        ) : null}
      </View>
      {open && suggestions.length > 0 ? (
        <View style={styles.dropdown}>
          {suggestions.map((port, i) => (
            <Pressable
              key={`${port.code ?? port.name}-${i}`}
              onPress={() => select(port)}
              style={({ pressed }) => [
                styles.option,
                i < suggestions.length - 1 && styles.optionBorder,
                pressed && styles.optionPressed,
              ]}
            >
              <View style={styles.optionRow}>
                <Text style={styles.optionName} numberOfLines={1}>
                  {port.name}
                </Text>
                {port.code ? (
                  <Text style={styles.code}>{String(port.code).toUpperCase()}</Text>
                ) : null}
              </View>
              {port.country_name || port.country ? (
                <Text style={styles.country}>{port.country_name || port.country}</Text>
              ) : null}
            </Pressable>
          ))}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1 },
  label: {
    color: palette.textSecondary,
    fontSize: 11.5,
    fontWeight: '600',
    letterSpacing: 0.3,
    marginBottom: 6,
  },
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
  spinner: { position: 'absolute', right: 12, top: 14 },
  dropdown: {
    marginTop: 6,
    borderRadius: 13,
    backgroundColor: palette.cardHi,
    borderWidth: 1,
    borderColor: palette.border,
    overflow: 'hidden',
  },
  option: { paddingHorizontal: 14, paddingVertical: 10 },
  optionBorder: { borderBottomWidth: 1, borderBottomColor: palette.border },
  optionPressed: { backgroundColor: palette.inputBg },
  optionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  optionName: { color: palette.white, fontSize: 14, fontWeight: '600', flexShrink: 1 },
  code: {
    color: palette.blue,
    fontSize: 10,
    fontWeight: '700',
    backgroundColor: 'rgba(59,130,246,0.12)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 5,
    marginLeft: 8,
  },
  country: { color: palette.textMuted, fontSize: 12, marginTop: 2 },
});
