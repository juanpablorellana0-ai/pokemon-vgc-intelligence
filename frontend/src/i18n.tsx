import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';

type Lang = 'es' | 'en';

const dict = {
  es: {
    app_name: 'VGC Intelligence',
    tagline: 'Análisis competitivo VGC de nivel profesional.',
    coming_soon: 'Próximamente',
    coming_soon_body:
      'Estamos construyendo esta sección. Pronto tendrás datos, herramientas y análisis profundos aquí.',
    back_home: 'Volver al inicio',
    tab_home: 'Inicio',
    tab_meta: 'Meta',
    tab_tournaments: 'Torneos',
    tab_menu: 'Menú',
    home_hero_title: 'Centro de mando VGC',
    home_hero_sub: 'Métricas del meta, torneos y herramientas de equipo — en un solo lugar.',
    home_status_title: 'Estado de la plataforma',
    home_status_body:
      'Fundación de la aplicación lista. Fuentes de datos y motor de cálculo llegarán en próximas fases.',
    home_quick_access: 'Accesos rápidos',
    section_meta: 'Meta',
    section_tournaments: 'Torneos',
    section_teams: 'Equipos',
    section_team_builder: 'Team Builder',
    section_damage_calc: 'Calculadora de daño',
    section_analyzer: 'Analizador',
    section_vgc_guide: 'Guía VGC',
    menu_title: 'Herramientas',
    menu_subtitle: 'Elige una herramienta para empezar.',
    desc_meta: 'Uso, tendencias y núcleos del metagame.',
    desc_tournaments: 'Torneos oficiales y no oficiales.',
    desc_teams: 'Equipos importados y equipos de la comunidad.',
    desc_team_builder: 'Construye y valida tu equipo de 6.',
    desc_damage_calc: 'Cálculo determinista al estilo VGC.',
    desc_analyzer: 'Cobertura, debilidades y amenazas.',
    desc_vgc_guide: 'Fundamentos, formatos y estrategia.',
    section_pokedex: 'Pokédex',
    desc_pokedex: 'Datos canónicos de Pokémon Showdown.',
    live_badge: 'Disponible',
    px_search_placeholder: 'Buscar Pokémon…',
    px_all_types: 'Todos',
    px_only_base: 'Solo base',
    px_error: 'No se pudieron cargar los datos.',
    px_retry: 'Reintentar',
    px_empty: 'Sin resultados para tu búsqueda.',
    px_not_found: 'Pokémon no encontrado.',
    px_prev: 'Anterior',
    px_next: 'Siguiente',
    px_page: 'Página',
    px_results: 'resultados',
    px_base_stats: 'Estadísticas base',
    px_abilities: 'Habilidades',
    px_hidden: 'Oculta',
    px_moves: 'Movimientos',
    px_forms: 'Formas',
    px_height: 'Altura',
    px_weight: 'Peso',
    px_total: 'Total',
    lang_label: 'Idioma',
  },
  en: {
    app_name: 'VGC Intelligence',
    tagline: 'Professional-grade competitive VGC analytics.',
    coming_soon: 'Coming soon',
    coming_soon_body:
      "We're building this section. Data, tools and deep analytics will land here soon.",
    back_home: 'Back to home',
    tab_home: 'Home',
    tab_meta: 'Meta',
    tab_tournaments: 'Tournaments',
    tab_menu: 'Menu',
    home_hero_title: 'VGC command center',
    home_hero_sub: 'Meta insights, tournaments and team tools — in one place.',
    home_status_title: 'Platform status',
    home_status_body:
      'Application foundation ready. Data sources and calculation engine ship in upcoming phases.',
    home_quick_access: 'Quick access',
    section_meta: 'Meta',
    section_tournaments: 'Tournaments',
    section_teams: 'Teams',
    section_team_builder: 'Team Builder',
    section_damage_calc: 'Damage Calculator',
    section_analyzer: 'Analyzer',
    section_vgc_guide: 'VGC Guide',
    menu_title: 'Tools',
    menu_subtitle: 'Pick a tool to get started.',
    desc_meta: 'Usage, trends and metagame cores.',
    desc_tournaments: 'Official and non-official tournaments.',
    desc_teams: 'Imported and community teams.',
    desc_team_builder: 'Build and validate your team of 6.',
    desc_damage_calc: 'Deterministic VGC-style math.',
    desc_analyzer: 'Coverage, weaknesses and threats.',
    desc_vgc_guide: 'Fundamentals, formats and strategy.',
    section_pokedex: 'Pokédex',
    desc_pokedex: 'Canonical Pokémon Showdown data.',
    live_badge: 'Live',
    px_search_placeholder: 'Search Pokémon…',
    px_all_types: 'All',
    px_only_base: 'Base only',
    px_error: 'Could not load data.',
    px_retry: 'Retry',
    px_empty: 'No results for your search.',
    px_not_found: 'Pokémon not found.',
    px_prev: 'Prev',
    px_next: 'Next',
    px_page: 'Page',
    px_results: 'results',
    px_base_stats: 'Base stats',
    px_abilities: 'Abilities',
    px_hidden: 'Hidden',
    px_moves: 'Moves',
    px_forms: 'Forms',
    px_height: 'Height',
    px_weight: 'Weight',
    px_total: 'Total',
    lang_label: 'Language',
  },
} as const;

type Key = keyof (typeof dict)['en'];

interface Ctx {
  lang: Lang;
  t: (k: Key) => string;
  setLang: (l: Lang) => void;
  toggle: () => void;
}

const I18nCtx = createContext<Ctx | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>('es');
  const toggle = useCallback(() => setLang((l) => (l === 'es' ? 'en' : 'es')), []);
  const value = useMemo<Ctx>(
    () => ({
      lang,
      setLang,
      toggle,
      t: (k) => dict[lang][k],
    }),
    [lang, toggle],
  );
  return <I18nCtx.Provider value={value}>{children}</I18nCtx.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nCtx);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}
