import React from 'react';
import { SecondaryScreen } from '@/src/components/SecondaryScreen';
import { useI18n } from '@/src/i18n';

export default function VGCGuide() {
  const { t } = useI18n();
  return <SecondaryScreen testID="screen-vgc_guide" title={t('section_vgc_guide')} />;
}
