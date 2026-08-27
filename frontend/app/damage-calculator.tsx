import React from 'react';
import { SecondaryScreen } from '@/src/components/SecondaryScreen';
import { useI18n } from '@/src/i18n';

const IMG =
  'https://images.unsplash.com/photo-1762279388956-1c098163a2a8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NDh8MHwxfHNlYXJjaHwyfHxhYnN0cmFjdCUyMGRhdGElMjB2aXN1YWxpemF0aW9uJTIwZGFyayUyMGJsdWV8ZW58MHx8fHwxNzg3NzY5NjM2fDA&ixlib=rb-4.1.0&q=85';

export default function DamageCalculator() {
  const { t } = useI18n();
  return <SecondaryScreen testID="screen-damage_calc" title={t('section_damage_calc')} image={IMG} />;
}
