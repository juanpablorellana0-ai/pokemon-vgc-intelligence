import React from 'react';
import { ComingSoon } from '@/src/components/ComingSoon';
import { useI18n } from '@/src/i18n';

export default function MetaScreen() {
  const { t } = useI18n();
  return <ComingSoon testID="screen-meta" title={t('section_meta')} />;
}
