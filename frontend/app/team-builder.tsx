import React from 'react';
import { SecondaryScreen } from '@/src/components/SecondaryScreen';
import { useI18n } from '@/src/i18n';

export default function TeamBuilder() {
  const { t } = useI18n();
  return <SecondaryScreen testID="screen-team_builder" title={t('section_team_builder')} />;
}
