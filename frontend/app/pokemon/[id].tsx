import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { colors, spacing, radius, fontSize } from '@/src/theme';
import { useI18n } from '@/src/i18n';
import { PokemonSprite } from '@/src/components/PokemonSprite';
import {
  ApiError,
  apiGet,
  MoveEntry,
  PokemonAbilities,
  PokemonDetail,
  PokemonMoves,
} from '@/src/api/client';

const STAT_LABELS: [keyof PokemonDetail['base_stats'], string][] = [
  ['hp', 'HP'],
  ['atk', 'Atk'],
  ['def', 'Def'],
  ['spa', 'SpA'],
  ['spd', 'SpD'],
  ['spe', 'Spe'],
];
const STAT_MAX = 255;

export default function PokemonDetailScreen() {
  const { t } = useI18n();
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const [pokemon, setPokemon] = useState<PokemonDetail | null>(null);
  const [abilities, setAbilities] = useState<PokemonAbilities | null>(null);
  const [moves, setMoves] = useState<PokemonMoves | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    if (!id) return;
    setLoading(true);
    setError(false);
    setNotFound(false);
    Promise.all([
      apiGet<PokemonDetail>(`/pokemon/${encodeURIComponent(id)}`),
      apiGet<PokemonAbilities>(`/pokemon/${encodeURIComponent(id)}/abilities`),
      apiGet<PokemonMoves>(`/pokemon/${encodeURIComponent(id)}/moves`),
    ])
      .then(([p, a, m]) => {
        setPokemon(p);
        setAbilities(a);
        setMoves(m);
        setLoading(false);
      })
      .catch((e) => {
        if (e instanceof ApiError && e.status === 404) setNotFound(true);
        else setError(true);
        setLoading(false);
      });
  }, [id]);

  useEffect(load, [load]);

  const goBack = () => (router.canGoBack() ? router.back() : router.replace('/pokemon'));

  return (
    <SafeAreaView edges={['top']} style={styles.safe} testID="pokemon-detail">
      <View style={styles.topBar}>
        <Pressable
          testID="pokemon-detail-back"
          onPress={goBack}
          style={({ pressed }) => [styles.backBtn, pressed && { opacity: 0.8 }]}
          hitSlop={8}
        >
          <Ionicons name="chevron-back" size={22} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.topTitle} numberOfLines={1}>
          {pokemon?.name ?? t('section_pokedex')}
        </Text>
        <View style={styles.backBtn} />
      </View>

      {loading ? (
        <View style={styles.center} testID="detail-loading">
          <ActivityIndicator color={colors.brandPrimary} size="large" />
        </View>
      ) : notFound ? (
        <View style={styles.center} testID="detail-not-found">
          <Ionicons name="help-circle-outline" size={32} color={colors.onSurfaceSecondary} />
          <Text style={styles.stateText}>{t('px_not_found')}</Text>
          <Pressable onPress={goBack} style={({ pressed }) => [styles.retryBtn, pressed && { opacity: 0.85 }]}>
            <Text style={styles.retryText}>{t('back_home')}</Text>
          </Pressable>
        </View>
      ) : error || !pokemon ? (
        <View style={styles.center} testID="detail-error">
          <Ionicons name="cloud-offline-outline" size={32} color={colors.onSurfaceSecondary} />
          <Text style={styles.stateText}>{t('px_error')}</Text>
          <Pressable testID="detail-retry" onPress={load} style={({ pressed }) => [styles.retryBtn, pressed && { opacity: 0.85 }]}>
            <Text style={styles.retryText}>{t('px_retry')}</Text>
          </Pressable>
        </View>
      ) : (
        <FlatList
          testID="detail-scroll"
          data={moves?.items ?? []}
          keyExtractor={(m) => m.showdown_id}
          contentContainerStyle={styles.listContent}
          ListHeaderComponent={
            <DetailHeader pokemon={pokemon} abilities={abilities} movesTotal={moves?.total ?? 0} t={t} />
          }
          renderItem={({ item }) => <MoveRow move={item} />}
        />
      )}
    </SafeAreaView>
  );
}

function DetailHeader({ pokemon, abilities, movesTotal, t }: {
  pokemon: PokemonDetail;
  abilities: PokemonAbilities | null;
  movesTotal: number;
  t: (k: any) => string;
}) {
  const statTotal = STAT_LABELS.reduce((acc, [k]) => acc + (pokemon.base_stats?.[k] ?? 0), 0);
  return (
    <View style={{ gap: spacing.lg }}>
      {/* Identity */}
      <View style={styles.card}>
        <View style={styles.identityRow}>
          <View style={{ flex: 1, gap: spacing.sm }}>
            <Text style={styles.dexNum}>#{String(pokemon.num).padStart(4, '0')}</Text>
            <Text style={styles.name} testID="detail-name">{pokemon.name}</Text>
            <View style={styles.typeRow}>
              {pokemon.types.map((ty) => (
                <View key={ty} style={styles.typeChip} testID={`detail-type-${ty.toLowerCase()}`}>
                  <Text style={styles.typeChipText}>{ty}</Text>
                </View>
              ))}
            </View>
          </View>
          <PokemonSprite
            uri={pokemon.image_url}
            fallbackUri={pokemon.image_fallback_url}
            size={96}
            testID="detail-sprite"
          />
        </View>
        <View style={styles.metaRow}>
          {pokemon.height_m != null && (
            <Text style={styles.metaText}>{t('px_height')}: {pokemon.height_m} m</Text>
          )}
          {pokemon.weight_kg != null && (
            <Text style={styles.metaText}>{t('px_weight')}: {pokemon.weight_kg} kg</Text>
          )}
        </View>
        {(pokemon.forme || pokemon.other_formes.length > 0) && (
          <View style={{ gap: 2 }}>
            <Text style={styles.sectionSub}>{t('px_forms')}</Text>
            {pokemon.forme && (
              <Text style={styles.metaText}>
                {pokemon.base_species_name ?? ''} · {pokemon.forme}
              </Text>
            )}
            {pokemon.other_formes.length > 0 && (
              <Text style={styles.metaText}>{pokemon.other_formes.join(', ')}</Text>
            )}
          </View>
        )}
      </View>

      {/* Base stats */}
      <View style={styles.card} testID="detail-stats">
        <Text style={styles.sectionTitle}>{t('px_base_stats')}</Text>
        {STAT_LABELS.map(([key, label]) => {
          const v = pokemon.base_stats?.[key] ?? 0;
          return (
            <View key={key} style={styles.statRow}>
              <Text style={styles.statLabel}>{label}</Text>
              <Text style={styles.statValue}>{v}</Text>
              <View style={styles.statTrack}>
                <View style={[styles.statFill, { width: `${Math.min(100, (v / STAT_MAX) * 100)}%` }]} />
              </View>
            </View>
          );
        })}
        <View style={styles.statRow}>
          <Text style={[styles.statLabel, { fontWeight: '800' }]}>{t('px_total')}</Text>
          <Text style={[styles.statValue, { fontWeight: '800' }]}>{statTotal}</Text>
          <View style={styles.statTrack} />
        </View>
      </View>

      {/* Abilities */}
      <View style={styles.card} testID="detail-abilities">
        <Text style={styles.sectionTitle}>{t('px_abilities')}</Text>
        {(abilities?.items ?? []).map((slot) => (
          <View key={slot.slot} style={styles.abilityRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.abilityName}>{slot.name}</Text>
              {slot.ability?.short_desc ? (
                <Text style={styles.metaText}>{slot.ability.short_desc}</Text>
              ) : null}
            </View>
            {slot.is_hidden && (
              <View style={styles.hiddenBadge}>
                <Text style={styles.hiddenBadgeText}>{t('px_hidden').toUpperCase()}</Text>
              </View>
            )}
          </View>
        ))}
      </View>

      {/* Moves header */}
      <Text style={styles.sectionTitle} testID="detail-moves-title">
        {t('px_moves')} ({movesTotal})
      </Text>
    </View>
  );
}

function MoveRow({ move }: { move: MoveEntry }) {
  return (
    <View style={styles.moveRow} testID={`move-row-${move.showdown_id}`}>
      <View style={{ flex: 1 }}>
        <Text style={styles.moveName}>{move.name}</Text>
        <Text style={styles.metaText}>
          {move.type} · {move.category}
          {typeof move.base_power === 'number' && move.base_power > 0 ? ` · ${move.base_power} BP` : ''}
          {typeof move.accuracy === 'number' ? ` · ${move.accuracy}%` : ''}
        </Text>
      </View>
      <Text style={styles.movePP}>{move.pp != null ? `PP ${move.pp}` : ''}</Text>
    </View>
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
  listContent: { padding: spacing.lg, gap: spacing.sm, paddingBottom: spacing.xxxl },
  card: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  dexNum: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, fontWeight: '700' },
  identityRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  name: { color: colors.onSurface, fontSize: fontSize.display, fontWeight: '800', letterSpacing: -0.5 },
  typeRow: { flexDirection: 'row', gap: spacing.sm },
  typeChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    backgroundColor: colors.brandTertiary,
    borderWidth: 1,
    borderColor: colors.brandPrimary,
  },
  typeChipText: { color: colors.onBrandTertiary, fontSize: fontSize.sm, fontWeight: '700', letterSpacing: 0.5 },
  metaRow: { flexDirection: 'row', gap: spacing.lg },
  metaText: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, lineHeight: 18 },
  sectionTitle: { color: colors.onSurface, fontSize: fontSize.lg, fontWeight: '800', letterSpacing: -0.3 },
  sectionSub: { color: colors.onSurface, fontSize: fontSize.base, fontWeight: '700', marginTop: spacing.xs },
  statRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  statLabel: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, fontWeight: '700', width: 40 },
  statValue: { color: colors.onSurface, fontSize: fontSize.sm, fontWeight: '700', width: 36, textAlign: 'right' },
  statTrack: {
    flex: 1,
    height: 8,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceTertiary,
    overflow: 'hidden',
  },
  statFill: { height: '100%', borderRadius: radius.pill, backgroundColor: colors.brandPrimary },
  abilityRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  abilityName: { color: colors.onSurface, fontSize: fontSize.base, fontWeight: '700' },
  hiddenBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.brandSecondary,
  },
  hiddenBadgeText: { color: colors.brandSecondary, fontSize: 9, fontWeight: '800', letterSpacing: 1 },
  moveRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  moveName: { color: colors.onSurface, fontSize: fontSize.base, fontWeight: '700' },
  movePP: { color: colors.onSurfaceSecondary, fontSize: fontSize.sm, fontWeight: '600' },
});
