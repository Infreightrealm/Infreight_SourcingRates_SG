/**
 * QuoteCard — one card per carrier result. Collapsed shows the best rate +
 * key meta and a status badge; tapping expands the charge breakdown. Carriers
 * needing human 2FA surface a "Solve" action.
 */
import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { CARRIERS, statusStyle } from '@/constants/api';
import { brandGradient, carrierColors, palette } from '@/theme/colors';
import type { CarrierResultSchema } from '@/types/api';
import { bestQuote, money } from '@/utils/quotes';

const MANUAL_STATUSES = new Set([
  'WAITING_FOR_HUMAN_VERIFICATION',
  'CAPTCHA_OR_MANUAL_REVIEW_REQUIRED',
  'MANUAL_ACTION_REQUIRED',
  'BOT_CHALLENGE_DETECTED',
]);

interface Props {
  result: CarrierResultSchema;
  onSolve?: (carrier: string) => void;
}

function carrierName(code: string): string {
  return CARRIERS.find((c) => c.code === code)?.name ?? code;
}

export default function QuoteCard({ result, onSolve }: Props) {
  const [expanded, setExpanded] = useState(false);
  const badge = statusStyle(result.status);
  const accent = carrierColors[result.carrier] ?? palette.textMuted;
  const quote = bestQuote(result.quotes);
  const needsSolve = MANUAL_STATUSES.has(result.status);
  const canExpand = !!quote;

  return (
    <View style={styles.card}>
      <View style={[styles.accent, { backgroundColor: accent }]} />

      <Pressable
        disabled={!canExpand}
        onPress={() => setExpanded((e) => !e)}
        style={styles.body}
      >
        <View style={styles.headerRow}>
          <Text style={styles.carrier}>{carrierName(result.carrier)}</Text>
          <View style={[styles.badge, { backgroundColor: badge.bg }]}>
            <View style={[styles.badgeDot, { backgroundColor: badge.color }]} />
            <Text style={[styles.badgeText, { color: badge.color }]}>{badge.label}</Text>
          </View>
        </View>

        {quote ? (
          <>
            <View style={styles.priceRow}>
              <Text style={styles.price}>{money(quote.final_freight_value, quote.currency)}</Text>
              <Text style={styles.currency}>{quote.currency}</Text>
            </View>
            <View style={styles.metaRow}>
              <Meta label="Transit" value={quote.transit_time_days ? `${quote.transit_time_days} days` : '—'} />
              <Meta label="Routing" value={quote.routing || 'Direct'} />
              <Meta label="Free time" value={quote.free_time ? `${quote.free_time} days` : '—'} />
            </View>
            <Text style={styles.expandHint}>{expanded ? 'Tap to collapse' : 'Tap for charge breakdown'}</Text>
          </>
        ) : (
          <Text style={styles.note}>
            {result.error_message || badge.label}
          </Text>
        )}
      </Pressable>

      {needsSolve ? (
        <Pressable
          onPress={() => onSolve?.(result.carrier)}
          style={({ pressed }) => [styles.solveWrap, pressed && styles.solvePressed]}
        >
          <LinearGradient
            colors={brandGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.solveBtn}
          >
            <Text style={styles.solveText}>Solve 2FA</Text>
          </LinearGradient>
        </Pressable>
      ) : null}

      {expanded && quote ? (
        <View style={styles.breakdown}>
          <Text style={styles.breakdownTitle}>CHARGE BREAKDOWN</Text>
          <ChargeRow name="Basic Ocean Freight" amount={money(quote.basic_ocean_freight, quote.currency)} />
          {quote.discount ? (
            <ChargeRow
              name="Discount"
              amount={`−${money(Math.abs(quote.discount), quote.currency)}`}
              color={palette.emerald}
            />
          ) : null}
          {quote.included_freight_surcharges.map((ch, i) => (
            <ChargeRow key={`${ch.name}-${i}`} name={ch.name} amount={money(ch.amount, ch.currency)} />
          ))}
          <View style={styles.divider} />
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Final Freight Value</Text>
            <Text style={styles.totalValue}>{money(quote.final_freight_value, quote.currency)}</Text>
          </View>
        </View>
      ) : null}
    </View>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.meta}>
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={styles.metaValue}>{value}</Text>
    </View>
  );
}

function ChargeRow({ name, amount, color }: { name: string; amount: string; color?: string }) {
  return (
    <View style={styles.chargeRow}>
      <Text style={styles.chargeName} numberOfLines={1}>{name}</Text>
      <Text style={[styles.chargeAmount, color ? { color } : null]}>{amount}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: palette.card,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    overflow: 'hidden',
  },
  accent: { position: 'absolute', left: 0, top: 14, bottom: 14, width: 4, borderRadius: 2 },
  body: { paddingVertical: 14, paddingLeft: 18, paddingRight: 14 },
  headerRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  carrier: { color: palette.white, fontSize: 15.5, fontWeight: '700', flexShrink: 1 },
  badge: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 10, height: 22, borderRadius: 11 },
  badgeDot: { width: 6, height: 6, borderRadius: 3 },
  badgeText: { fontSize: 11, fontWeight: '600' },
  priceRow: { flexDirection: 'row', alignItems: 'flex-end', gap: 6, marginTop: 10 },
  price: { color: palette.white, fontSize: 26, fontWeight: '800', letterSpacing: -0.5 },
  currency: { color: palette.textMuted, fontSize: 11.5, fontWeight: '600', marginBottom: 4 },
  metaRow: { flexDirection: 'row', marginTop: 12, gap: 8 },
  meta: { flex: 1 },
  metaLabel: { color: palette.textMuted, fontSize: 10.5 },
  metaValue: { color: palette.white, fontSize: 13, fontWeight: '600', marginTop: 3 },
  expandHint: { color: palette.textMuted, fontSize: 11, marginTop: 12 },
  note: { color: palette.textSecondary, fontSize: 12.5, marginTop: 8 },
  solveWrap: { marginHorizontal: 14, marginBottom: 14, borderRadius: 14, overflow: 'hidden' },
  solvePressed: { opacity: 0.9 },
  solveBtn: { height: 40, alignItems: 'center', justifyContent: 'center' },
  solveText: { color: '#fff', fontSize: 13, fontWeight: '700' },
  breakdown: { paddingHorizontal: 18, paddingBottom: 16, paddingTop: 4 },
  breakdownTitle: { color: palette.textMuted, fontSize: 10, fontWeight: '700', letterSpacing: 1, marginBottom: 10 },
  chargeRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 9 },
  chargeName: { color: palette.textSecondary, fontSize: 13, flexShrink: 1, marginRight: 12 },
  chargeAmount: { color: palette.white, fontSize: 13, fontWeight: '600' },
  divider: { height: 1, backgroundColor: palette.border, marginVertical: 8 },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  totalLabel: { color: palette.white, fontSize: 13.5, fontWeight: '700' },
  totalValue: { color: palette.emerald, fontSize: 15, fontWeight: '800' },
});
