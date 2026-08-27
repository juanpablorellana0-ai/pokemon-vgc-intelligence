import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Image } from 'expo-image';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, fontSize } from '../theme';
import { useI18n } from '../i18n';

interface Props {
  title: string;
  image?: string;
  testID?: string;
}

const DEFAULT_IMAGE =
  'https://images.unsplash.com/photo-1689443111130-6e9c7dfd8f9e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHxhYnN0cmFjdCUyMGdlb21ldHJpYyUyMGRhcmslMjBjeWJlciUyMGJhY2tncm91bmQlMjBwdXJwbGV8ZW58MHx8fHwxNzg3NzY5NjM2fDA&ixlib=rb-4.1.0&q=85';

export function ComingSoon({ title, image, testID }: Props) {
  const { t } = useI18n();
  const router = useRouter();
  return (
    <View style={styles.root} testID={testID ?? 'coming-soon'}>
      <Image
        source={{ uri: image ?? DEFAULT_IMAGE }}
        style={StyleSheet.absoluteFill}
        contentFit="cover"
        transition={200}
      />
      <LinearGradient
        colors={['rgba(11,14,20,0.65)', 'rgba(11,14,20,0.95)', colors.surface]}
        locations={[0, 0.6, 1]}
        style={StyleSheet.absoluteFill}
      />
      <View style={styles.content}>
        <View style={styles.badge} testID="coming-soon-badge">
          <View style={styles.dot} />
          <Text style={styles.badgeText}>{t('coming_soon').toUpperCase()}</Text>
        </View>
        <Text style={styles.title} testID="coming-soon-title">{title}</Text>
        <Text style={styles.body} testID="coming-soon-body">{t('coming_soon_body')}</Text>
        <Pressable
          testID="coming-soon-back-btn"
          onPress={() => router.replace('/(tabs)')}
          style={({ pressed }) => [styles.cta, pressed && { opacity: 0.85 }]}
        >
          <Ionicons name="arrow-back" size={16} color={colors.onBrandPrimary} />
          <Text style={styles.ctaText}>{t('back_home')}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  content: {
    flex: 1,
    justifyContent: 'flex-end',
    padding: spacing.xl,
    gap: spacing.md,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.brandPrimary,
    backgroundColor: 'rgba(99,102,241,0.12)',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.brandPrimary,
  },
  badgeText: {
    color: colors.onBrandTertiary,
    fontSize: fontSize.sm,
    letterSpacing: 1.5,
    fontWeight: '700',
  },
  title: {
    color: colors.onSurface,
    fontSize: fontSize.display,
    fontWeight: '800',
    letterSpacing: -0.5,
  },
  body: {
    color: colors.onSurfaceSecondary,
    fontSize: fontSize.lg,
    lineHeight: 22,
    maxWidth: 520,
  },
  cta: {
    marginTop: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    alignSelf: 'flex-start',
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
  },
  ctaText: {
    color: colors.onBrandPrimary,
    fontWeight: '700',
    fontSize: fontSize.base,
  },
});
