import React from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable } from 'react-native';
import { Image } from 'expo-image';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, fontSize } from '@/src/theme';
import { useI18n } from '@/src/i18n';
import { LangToggle } from '@/src/components/LangToggle';

const HERO =
  'https://images.unsplash.com/photo-1778957489702-6455b42cf3eb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1OTV8MHwxfHNlYXJjaHw0fHxlc3BvcnRzJTIwc3RhZGl1bSUyMGRhcmslMjBhcmVuYXxlbnwwfHx8fDE3ODc3Njk2MzZ8MA&ixlib=rb-4.1.0&q=85';

type QAKey =
  | 'pokedex'
  | 'meta'
  | 'tournaments'
  | 'teams'
  | 'team_builder'
  | 'damage_calc'
  | 'analyzer'
  | 'vgc_guide';

interface QA {
  key: QAKey;
  label: string;
  desc: string;
  icon: keyof typeof Ionicons.glyphMap;
  href: string;
  live?: boolean;
}

export default function Home() {
  const { t } = useI18n();
  const router = useRouter();

  const quickAccess: QA[] = [
    { key: 'pokedex', label: t('section_pokedex'), desc: t('desc_pokedex'), icon: 'search-outline', href: '/pokemon', live: true },
    { key: 'meta', label: t('section_meta'), desc: t('desc_meta'), icon: 'stats-chart-outline', href: '/(tabs)/meta' },
    { key: 'tournaments', label: t('section_tournaments'), desc: t('desc_tournaments'), icon: 'trophy-outline', href: '/(tabs)/tournaments' },
    { key: 'teams', label: t('section_teams'), desc: t('desc_teams'), icon: 'people-outline', href: '/teams' },
    { key: 'team_builder', label: t('section_team_builder'), desc: t('desc_team_builder'), icon: 'construct-outline', href: '/team-builder' },
    { key: 'damage_calc', label: t('section_damage_calc'), desc: t('desc_damage_calc'), icon: 'calculator-outline', href: '/damage-calculator' },
    { key: 'analyzer', label: t('section_analyzer'), desc: t('desc_analyzer'), icon: 'pulse-outline', href: '/analyzer' },
    { key: 'vgc_guide', label: t('section_vgc_guide'), desc: t('desc_vgc_guide'), icon: 'book-outline', href: '/vgc-guide' },
  ];

  return (
    <SafeAreaView edges={['top']} style={styles.safe} testID="home-screen">
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <View style={styles.brandRow}>
            <View style={styles.logoDot} />
            <Text style={styles.brand} testID="app-brand">{t('app_name')}</Text>
          </View>
          <LangToggle />
        </View>

        <View style={styles.hero} testID="home-hero">
          <Image source={{ uri: HERO }} style={StyleSheet.absoluteFill} contentFit="cover" transition={200} />
          <LinearGradient
            colors={['rgba(11,14,20,0.25)', 'rgba(11,14,20,0.85)', colors.surface]}
            locations={[0, 0.7, 1]}
            style={StyleSheet.absoluteFill}
          />
          <View style={styles.heroBody}>
            <View style={styles.tag}>
              <View style={styles.tagDot} />
              <Text style={styles.tagText}>VGC · REG G</Text>
            </View>
            <Text style={styles.heroTitle}>{t('home_hero_title')}</Text>
            <Text style={styles.heroSub}>{t('home_hero_sub')}</Text>
          </View>
        </View>

        <View style={styles.card} testID="home-status-card">
          <View style={styles.cardHeader}>
            <Ionicons name="shield-checkmark-outline" size={16} color={colors.brandPrimary} />
            <Text style={styles.cardTitle}>{t('home_status_title')}</Text>
          </View>
          <Text style={styles.cardBody}>{t('home_status_body')}</Text>
          <View style={styles.pillsRow}>
            <StatusPill label="API v1" ok />
            <StatusPill label="DB" ok />
            <StatusPill label="Ingest" ok={false} />
            <StatusPill label="Calc" ok={false} />
          </View>
        </View>

        <Text style={styles.sectionTitle}>{t('home_quick_access')}</Text>
        <View style={styles.grid}>
          {quickAccess.map((q) => (
            <View key={q.key} style={styles.tileWrap}>
              <Pressable
                testID={`quick-access-${q.key}`}
                onPress={() => router.push(q.href as any)}
                style={({ pressed }) => [styles.tile, pressed && styles.tilePressed]}
              >
                <View style={styles.tileIcon}>
                  <Ionicons name={q.icon} size={20} color={colors.brandPrimary} />
                </View>
                <Text style={styles.tileLabel}>{q.label}</Text>
                <Text style={styles.tileDesc} numberOfLines={2}>{q.desc}</Text>
                <View style={styles.tileFooter}>
                  <Text style={[styles.soon, q.live && styles.liveBadge]}>
                    {(q.live ? t('live_badge') : t('coming_soon')).toUpperCase()}
                  </Text>
                  <Ionicons name="arrow-forward" size={14} color={colors.onSurfaceSecondary} />
                </View>
              </Pressable>
            </View>
          ))}
        </View>

        <View style={{ height: spacing.xxxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

function StatusPill({ label, ok }: { label: string; ok: boolean }) {
  return (
    <View
      style={[styles.pill, { borderColor: ok ? colors.success : colors.borderStrong }]}
      testID={`status-${label.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <View style={[styles.pillDot, { backgroundColor: ok ? colors.success : colors.onSurfaceSecondary }]} />
      <Text style={[styles.pillText, { color: ok ? colors.onSurface : colors.onSurfaceSecondary }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.surface },
  scroll: { paddingBottom: spacing.xl },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  brandRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  logoDot: {
    width: 10, height: 10, borderRadius: 2,
    backgroundColor: colors.brandPrimary,
    transform: [{ rotate: '45deg' }],
  },
  brand: { color: colors.onSurface, fontSize: fontSize.lg, fontWeight: '800', letterSpacing: 0.5 },
  hero: {
    marginHorizontal: spacing.lg,
    borderRadius: radius.lg,
    overflow: 'hidden',
    height: 220,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'flex-end',
  },
  heroBody: { padding: spacing.lg, gap: spacing.sm },
  tag: {
    flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start',
    gap: 6, paddingHorizontal: spacing.sm + 2, paddingVertical: 4,
    borderRadius: radius.pill, borderWidth: 1, borderColor: colors.brandPrimary,
    backgroundColor: 'rgba(99,102,241,0.15)',
  },
  tagDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: colors.brandPrimary },
  tagText: { color: colors.onBrandTertiary, fontSize: 10, fontWeight: '800', letterSpacing: 1.5 },
  heroTitle: { color: colors.onSurface, fontSize: fontSize.xxl + 2, fontWeight: '800', letterSpacing: -0.5 },
  heroSub: { color: colors.onSurfaceSecondary, fontSize: fontSize.base, lineHeight: 20 },
  card: {
    marginTop: spacing.lg,
    marginHorizontal: spacing.lg,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  cardTitle: { color: colors.onSurface, fontSize: fontSize.base, fontWeight: '700' },
  cardBody: { color: colors.onSurfaceSecondary, fontSize: fontSize.base, lineHeight: 20 },
  pillsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.xs },
  pill: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: spacing.md, paddingVertical: 6,
    borderRadius: radius.pill, borderWidth: 1,
    backgroundColor: colors.surfaceTertiary,
  },
  pillDot: { width: 6, height: 6, borderRadius: 3 },
  pillText: { fontSize: fontSize.sm, fontWeight: '700', letterSpacing: 0.5 },
  sectionTitle: {
    color: colors.onSurface,
    fontSize: fontSize.lg,
    fontWeight: '800',
    marginTop: spacing.xl,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
    letterSpacing: -0.3,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.lg - spacing.xs,
  },
  tileWrap: {
    width: '50%',
    padding: spacing.xs,
  },
  tile: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.sm,
    minHeight: 150,
  },
  tilePressed: {
    opacity: 0.9,
    borderColor: colors.brandPrimary,
  },
  tileIcon: {
    width: 36, height: 36, borderRadius: radius.sm,
    backgroundColor: colors.brandTertiary,
    alignItems: 'center', justifyContent: 'center',
  },
  tileLabel: { color: colors.onSurface, fontSize: fontSize.base, fontWeight: '700' },
  tileDesc: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, lineHeight: 16 },
  tileFooter: {
    marginTop: 'auto',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  soon: {
    color: colors.brandSecondary,
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.2,
  },
  liveBadge: {
    color: colors.success,
  },
});
