/**
 * Design tokens generated from /app/design_guidelines.json.
 * Kept as plain constants so we don't ship a runtime theme provider.
 */
export const colors = {
  surface: '#0B0E14',
  onSurface: '#F1F5F9',
  surfaceSecondary: '#151A23',
  onSurfaceSecondary: '#94A3B8',
  surfaceTertiary: '#1E2532',
  onSurfaceTertiary: '#CBD5E1',
  brand: '#4F46E5',
  brandPrimary: '#6366F1',
  onBrandPrimary: '#FFFFFF',
  brandSecondary: '#8B5CF6',
  brandTertiary: '#1E1B4B',
  onBrandTertiary: '#A5B4FC',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  border: '#1E293B',
  borderStrong: '#334155',
  divider: '#1E293B',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
} as const;

export const radius = {
  sm: 6,
  md: 12,
  lg: 20,
  pill: 999,
} as const;

export const fontSize = {
  sm: 12,
  base: 14,
  lg: 16,
  xl: 20,
  xxl: 24,
  display: 28,
} as const;

export const font = {
  display: 'System', // fallback; Rajdhani not bundled to avoid deps
  text: 'System',
} as const;
