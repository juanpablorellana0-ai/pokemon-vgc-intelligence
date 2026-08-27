import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, fontSize } from '../theme';
import { useI18n } from '../i18n';

/** Compact language switch used in the top header. */
export function LangToggle() {
  const { lang, toggle, t } = useI18n();
  return (
    <Pressable
      testID="lang-toggle-button"
      onPress={toggle}
      style={({ pressed }) => [styles.root, pressed && { opacity: 0.8 }]}
      accessibilityLabel={t('lang_label')}
    >
      <Ionicons name="globe-outline" size={14} color={colors.onSurfaceSecondary} />
      <Text style={styles.text}>{lang.toUpperCase()}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  root: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs + 2,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
  },
  text: {
    color: colors.onSurfaceSecondary,
    fontSize: fontSize.sm,
    fontWeight: '700',
    letterSpacing: 1,
  },
});
