import React from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, fontSize } from '@/src/theme';
import { useI18n } from '@/src/i18n';
import { LangToggle } from '@/src/components/LangToggle';

type Key = 'teams' | 'team_builder' | 'damage_calc' | 'analyzer' | 'vgc_guide';

interface Row {
  key: Key;
  label: string;
  desc: string;
  icon: keyof typeof Ionicons.glyphMap;
  href: string;
}

export default function MenuScreen() {
  const { t } = useI18n();
  const router = useRouter();

  const rows: Row[] = [
    { key: 'teams', label: t('section_teams'), desc: t('desc_teams'), icon: 'people-outline', href: '/teams' },
    { key: 'team_builder', label: t('section_team_builder'), desc: t('desc_team_builder'), icon: 'construct-outline', href: '/team-builder' },
    { key: 'damage_calc', label: t('section_damage_calc'), desc: t('desc_damage_calc'), icon: 'calculator-outline', href: '/damage-calculator' },
    { key: 'analyzer', label: t('section_analyzer'), desc: t('desc_analyzer'), icon: 'pulse-outline', href: '/analyzer' },
    { key: 'vgc_guide', label: t('section_vgc_guide'), desc: t('desc_vgc_guide'), icon: 'book-outline', href: '/vgc-guide' },
  ];

  return (
    <SafeAreaView edges={['top']} style={styles.safe} testID="menu-screen">
      <View style={styles.header}>
        <Text style={styles.title}>{t('menu_title')}</Text>
        <LangToggle />
      </View>
      <Text style={styles.subtitle}>{t('menu_subtitle')}</Text>
      <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
        {rows.map((r) => (
          <Pressable
            key={r.key}
            testID={`menu-row-${r.key}`}
            onPress={() => router.push(r.href as any)}
            style={({ pressed }) => [styles.row, pressed && styles.rowPressed]}
          >
            <View style={styles.rowIcon}>
              <Ionicons name={r.icon} size={22} color={colors.brandPrimary} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.rowLabel}>{r.label}</Text>
              <Text style={styles.rowDesc}>{r.desc}</Text>
            </View>
            <Ionicons name="chevron-forward" size={18} color={colors.onSurfaceSecondary} />
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.surface },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
  },
  title: { color: colors.onSurface, fontSize: fontSize.xxl, fontWeight: '800', letterSpacing: -0.5 },
  subtitle: {
    color: colors.onSurfaceSecondary,
    fontSize: fontSize.base,
    paddingHorizontal: spacing.lg,
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
  },
  list: { paddingHorizontal: spacing.lg, gap: spacing.md, paddingBottom: spacing.xl },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    padding: spacing.lg,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  rowPressed: { borderColor: colors.brandPrimary, opacity: 0.9 },
  rowIcon: {
    width: 44, height: 44, borderRadius: radius.sm,
    backgroundColor: colors.brandTertiary,
    alignItems: 'center', justifyContent: 'center',
  },
  rowLabel: { color: colors.onSurface, fontSize: fontSize.lg, fontWeight: '700' },
  rowDesc: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, marginTop: 2 },
});
