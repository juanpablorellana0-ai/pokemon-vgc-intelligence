import React from 'react';
import { ComingSoon } from '@/src/components/ComingSoon';
import { useI18n } from '@/src/i18n';

const IMG =
  'https://images.unsplash.com/photo-1778957489702-6455b42cf3eb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1OTV8MHwxfHNlYXJjaHw0fHxlc3BvcnRzJTIwc3RhZGl1bSUyMGRhcmslMjBhcmVuYXxlbnwwfHx8fDE3ODc3Njk2MzZ8MA&ixlib=rb-4.1.0&q=85';

export default function TournamentsScreen() {
  const { t } = useI18n();
  return <ComingSoon testID="screen-tournaments" title={t('section_tournaments')} image={IMG} />;
}
