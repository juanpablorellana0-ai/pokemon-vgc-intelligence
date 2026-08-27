import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, fontSize } from '@/src/theme';
import { ComingSoon } from '@/src/components/ComingSoon';
import { useI18n } from '@/src/i18n';

interface Props {
  title: string;
  testID: string;
  image?: string;
}

export function SecondaryScreen({ title, testID, image }: Props) {
  const router = useRouter();
  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      <View style={styles.topBar}>
        <Pressable
          testID={`${testID}-back`}
          onPress={() => (router.canGoBack() ? router.back() : router.replace('/(tabs)'))}
          style={({ pressed }) => [styles.backBtn, pressed && { opacity: 0.8 }]}
          hitSlop={8}
        >
          <Ionicons name="chevron-back" size={22} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.topTitle} numberOfLines={1}>{title}</Text>
        <View style={styles.backBtn} />
      </View>
      <View style={{ flex: 1 }}>
        <ComingSoon testID={testID} title={title} image={image} />
      </View>
    </SafeAreaView>
  );
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _unused() { void useI18n; }

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.surface },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.surface,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: radius.sm,
    alignItems: 'center', justifyContent: 'center',
  },
  topTitle: {
    color: colors.onSurface,
    fontSize: fontSize.lg,
    fontWeight: '700',
    letterSpacing: -0.3,
    flex: 1,
    textAlign: 'center',
  },
});
