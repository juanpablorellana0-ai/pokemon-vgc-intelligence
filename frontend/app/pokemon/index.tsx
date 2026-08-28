import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  TextInput,
  FlatList,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, fontSize } from '@/src/theme';
import { useI18n } from '@/src/i18n';
import { apiGet, Paged, PokemonSummary, TypeInfo } from '@/src/api/client';

const PAGE_SIZE = 50;

export default function PokemonExplorer() {
  const { t } = useI18n();
  const router = useRouter();

  const [search, setSearch] = useState('');
  const [debounced, setDebounced] = useState('');
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const [onlyBase, setOnlyBase] = useState(false);
  const [page, setPage] = useState(1); // 1-based
  const [data, setData] = useState<Paged<PokemonSummary> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [types, setTypes] = useState<string[]>([]);
  const requestSeq = useRef(0);

  // debounce search input
  useEffect(() => {
    const h = setTimeout(() => setDebounced(search.trim()), 350);
    return () => clearTimeout(h);
  }, [search]);

  // reset page when the query changes
  useEffect(() => {
    setPage(1);
  }, [debounced, typeFilter, onlyBase]);

  // type filter chips (from canonical /types)
  useEffect(() => {
    apiGet<Paged<TypeInfo>>('/types', { limit: 25 })
      .then((res) => setTypes(res.items.map((x) => x.name).sort()))
      .catch(() => setTypes([]));
  }, []);

  const load = useCallback(() => {
    const seq = ++requestSeq.current;
    setLoading(true);
    setError(false);
    apiGet<Paged<PokemonSummary>>('/pokemon', {
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
      q: debounced || undefined,
      type: typeFilter ?? undefined,
      only_base: onlyBase || undefined,
    })
      .then((res) => {
        if (seq !== requestSeq.current) return;
        setData(res);
        setLoading(false);
      })
      .catch(() => {
        if (seq !== requestSeq.current) return;
        setError(true);
        setLoading(false);
      });
  }, [page, debounced, typeFilter, onlyBase]);

  useEffect(load, [load]);

  const pages = data?.pages ?? 0;

  return (
    <SafeAreaView edges={['top']} style={styles.safe} testID="pokemon-explorer">
      {/* Top bar */}
      <View style={styles.topBar}>
        <Pressable
          testID="pokemon-explorer-back"
          onPress={() => (router.canGoBack() ? router.back() : router.replace('/(tabs)'))}
          style={({ pressed }) => [styles.backBtn, pressed && { opacity: 0.8 }]}
          hitSlop={8}
        >
          <Ionicons name="chevron-back" size={22} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.topTitle} numberOfLines={1}>{t('section_pokedex')}</Text>
        <View style={styles.backBtn} />
      </View>

      {/* Search */}
      <View style={styles.searchRow}>
        <Ionicons name="search-outline" size={16} color={colors.onSurfaceSecondary} />
        <TextInput
          testID="pokemon-search-input"
          style={styles.searchInput}
          placeholder={t('px_search_placeholder')}
          placeholderTextColor={colors.onSurfaceSecondary}
          value={search}
          onChangeText={setSearch}
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="search"
        />
        {search.length > 0 && (
          <Pressable testID="pokemon-search-clear" onPress={() => setSearch('')} hitSlop={8}>
            <Ionicons name="close-circle" size={16} color={colors.onSurfaceSecondary} />
          </Pressable>
        )}
      </View>

      {/* Filters */}
      <View style={styles.filtersWrap}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          <Chip
            testID="filter-only-base"
            label={t('px_only_base')}
            active={onlyBase}
            onPress={() => setOnlyBase((v) => !v)}
          />
          <Chip
            testID="filter-type-all"
            label={t('px_all_types')}
            active={typeFilter === null}
            onPress={() => setTypeFilter(null)}
          />
          {types.map((ty) => (
            <Chip
              key={ty}
              testID={`filter-type-${ty.toLowerCase()}`}
              label={ty}
              active={typeFilter === ty}
              onPress={() => setTypeFilter((cur) => (cur === ty ? null : ty))}
            />
          ))}
        </ScrollView>
      </View>

      {/* Content */}
      {loading ? (
        <View style={styles.center} testID="pokemon-loading">
          <ActivityIndicator color={colors.brandPrimary} size="large" />
        </View>
      ) : error ? (
        <View style={styles.center} testID="pokemon-error">
          <Ionicons name="cloud-offline-outline" size={32} color={colors.onSurfaceSecondary} />
          <Text style={styles.stateText}>{t('px_error')}</Text>
          <Pressable testID="pokemon-retry" onPress={load} style={({ pressed }) => [styles.retryBtn, pressed && { opacity: 0.85 }]}>
            <Text style={styles.retryText}>{t('px_retry')}</Text>
          </Pressable>
        </View>
      ) : !data || data.items.length === 0 ? (
        <View style={styles.center} testID="pokemon-empty">
          <Ionicons name="search-outline" size={32} color={colors.onSurfaceSecondary} />
          <Text style={styles.stateText}>{t('px_empty')}</Text>
        </View>
      ) : (
        <FlatList
          testID="pokemon-list"
          data={data.items}
          keyExtractor={(item) => item.showdown_id}
          contentContainerStyle={styles.listContent}
          renderItem={({ item }) => (
            <Pressable
              testID={`pokemon-row-${item.showdown_id}`}
              onPress={() => router.push(`/pokemon/${item.showdown_id}` as any)}
              style={({ pressed }) => [styles.row, pressed && styles.rowPressed]}
            >
              <Text style={styles.rowNum}>#{String(item.num).padStart(4, '0')}</Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.rowName} numberOfLines={1}>{item.name}</Text>
                <View style={styles.typeRow}>
                  {item.types.map((ty) => (
                    <View key={ty} style={styles.typeChip}>
                      <Text style={styles.typeChipText}>{ty}</Text>
                    </View>
                  ))}
                </View>
              </View>
              <Ionicons name="chevron-forward" size={16} color={colors.onSurfaceSecondary} />
            </Pressable>
          )}
        />
      )}

      {/* Pager */}
      {!loading && !error && data && data.items.length > 0 && (
        <View style={styles.pager} testID="pokemon-pager">
          <Pressable
            testID="pager-prev"
            disabled={page <= 1}
            onPress={() => setPage((p) => Math.max(1, p - 1))}
            style={({ pressed }) => [styles.pagerBtn, page <= 1 && styles.pagerBtnDisabled, pressed && { opacity: 0.85 }]}
          >
            <Ionicons name="chevron-back" size={14} color={page <= 1 ? colors.onSurfaceSecondary : colors.onBrandPrimary} />
            <Text style={[styles.pagerBtnText, page <= 1 && styles.pagerBtnTextDisabled]}>{t('px_prev')}</Text>
          </Pressable>
          <Text style={styles.pagerInfo} testID="pager-info">
            {t('px_page')} {data.page} / {pages} · {data.total} {t('px_results')}
          </Text>
          <Pressable
            testID="pager-next"
            disabled={page >= pages}
            onPress={() => setPage((p) => Math.min(pages, p + 1))}
            style={({ pressed }) => [styles.pagerBtn, page >= pages && styles.pagerBtnDisabled, pressed && { opacity: 0.85 }]}
          >
            <Text style={[styles.pagerBtnText, page >= pages && styles.pagerBtnTextDisabled]}>{t('px_next')}</Text>
            <Ionicons name="chevron-forward" size={14} color={page >= pages ? colors.onSurfaceSecondary : colors.onBrandPrimary} />
          </Pressable>
        </View>
      )}
    </SafeAreaView>
  );
}

function Chip({ label, active, onPress, testID }: {
  label: string; active: boolean; onPress: () => void; testID?: string;
}) {
  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      style={({ pressed }) => [styles.chip, active && styles.chipActive, pressed && { opacity: 0.85 }]}
    >
      <Text style={[styles.chipText, active && styles.chipTextActive]}>{label}</Text>
    </Pressable>
  );
}

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
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginHorizontal: spacing.lg,
    marginTop: spacing.md,
    paddingHorizontal: spacing.md,
    height: 44,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
  },
  searchInput: {
    flex: 1,
    color: colors.onSurface,
    fontSize: fontSize.base,
    paddingVertical: 0,
  },
  filtersWrap: { marginTop: spacing.md },
  chipsRow: {
    paddingHorizontal: spacing.lg,
    gap: spacing.sm,
    alignItems: 'center',
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
  },
  chipActive: {
    borderColor: colors.brandPrimary,
    backgroundColor: colors.brandTertiary,
  },
  chipText: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, fontWeight: '600' },
  chipTextActive: { color: colors.onBrandTertiary },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.md,
    padding: spacing.xl,
  },
  stateText: { color: colors.onSurfaceSecondary, fontSize: fontSize.base, textAlign: 'center' },
  retryBtn: {
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
  },
  retryText: { color: colors.onBrandPrimary, fontWeight: '700', fontSize: fontSize.base },
  listContent: { padding: spacing.lg, gap: spacing.sm },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    minHeight: 56,
  },
  rowPressed: { borderColor: colors.brandPrimary, opacity: 0.9 },
  rowNum: {
    color: colors.onSurfaceSecondary,
    fontSize: fontSize.sm,
    fontWeight: '700',
    width: 52,
  },
  rowName: { color: colors.onSurface, fontSize: fontSize.base, fontWeight: '700' },
  typeRow: { flexDirection: 'row', gap: spacing.xs, marginTop: 2 },
  typeChip: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 1,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceTertiary,
    borderWidth: 1,
    borderColor: colors.borderStrong,
  },
  typeChipText: { color: colors.onSurfaceTertiary, fontSize: 10, fontWeight: '700', letterSpacing: 0.5 },
  pager: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surface,
  },
  pagerBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    minHeight: 36,
  },
  pagerBtnDisabled: { backgroundColor: colors.surfaceTertiary },
  pagerBtnText: { color: colors.onBrandPrimary, fontWeight: '700', fontSize: fontSize.sm },
  pagerBtnTextDisabled: { color: colors.onSurfaceSecondary },
  pagerInfo: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, fontWeight: '600' },
});
