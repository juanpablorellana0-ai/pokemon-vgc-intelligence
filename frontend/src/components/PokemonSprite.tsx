import React, { useEffect, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { Image } from 'expo-image';
import { colors, radius } from '../theme';

interface Props {
  uri?: string | null;
  fallbackUri?: string | null;
  size: number;
  testID?: string;
}

/**
 * Pokemon sprite with safe fallback: if the primary image fails to load,
 * it swaps to the API-provided fallback URL. The UI never breaks on a
 * missing image.
 */
export function PokemonSprite({ uri, fallbackUri, size, testID }: Props) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [uri]);
  const source = !failed && uri ? uri : fallbackUri;
  return (
    <View style={[styles.box, { width: size, height: size }]} testID={testID}>
      {source ? (
        <Image
          source={{ uri: source }}
          style={{ width: size, height: size }}
          contentFit="contain"
          transition={100}
          cachePolicy="memory-disk"
          onError={() => setFailed(true)}
        />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    borderRadius: radius.sm,
    backgroundColor: colors.surfaceTertiary,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
});
