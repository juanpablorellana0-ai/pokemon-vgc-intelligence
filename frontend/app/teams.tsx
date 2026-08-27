import React from 'react';
import { SecondaryScreen } from '@/src/components/SecondaryScreen';
import { useI18n } from '@/src/i18n';

export default function Teams() {
  const { t } = useI18n();
  return <SecondaryScreen testID="screen-teams" title={t('section_teams')} />;
}
