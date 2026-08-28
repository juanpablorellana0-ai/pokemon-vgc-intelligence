# VGC Intelligence — Guía de Frontend para Paola

> **Para quién es este documento:** Paola, diseñadora responsable de la UX/UI y la identidad visual de VGC Intelligence.
>
> **Qué necesitas saber antes de empezar:** Nada de backend. Esta guía explica todo lo que necesitas en lenguaje sencillo. Si algo no está claro, pregunta a Juan antes de asumir.
>
> **Última actualización:** Junio 2026. Fuente de verdad: el código real del repositorio (nada de lo documentado aquí está inventado; lo que aún no existe está marcado como **[FUTURO]** o **[PLANIFICADO]**).

---

## 1. Visión general del proyecto (Project Overview)

**VGC Intelligence** es una plataforma de análisis competitivo para jugadores de **Pokémon VGC** (Video Game Championships), el formato oficial de combates dobles 2 vs 2 de Pokémon.

**El problema que resuelve:** hoy, un jugador competitivo de VGC necesita saltar entre muchas webs distintas para:

- Ver qué Pokémon se están usando más en el metajuego (el "meta").
- Consultar datos de Pokémon: estadísticas, movimientos, habilidades, objetos.
- Construir y validar equipos de 6 Pokémon.
- Calcular daño entre Pokémon para planificar combates.
- Seguir torneos oficiales y sus clasificaciones.
- Estudiar equipos de jugadores profesionales.

VGC Intelligence unifica todo eso en **una sola aplicación** (móvil y web), con datos oficiales importados directamente de Pokémon Showdown (el simulador de referencia de la comunidad) y con un **coach de IA** (Claude) que analiza equipos y responde preguntas estratégicas.

---

## 2. Visión de producto (Product Vision)

A largo plazo, VGC Intelligence quiere ser **la herramienta profesional de referencia** para el análisis del metajuego VGC y la construcción competitiva de equipos:

- **Datos fiables y actualizados:** sincronización automática con las fuentes canónicas (Pokémon Showdown ya está integrado; otras fuentes competitivas llegarán en fases futuras).
- **Análisis del meta:** tendencias de uso, núcleos de equipos ("cores"), amenazas dominantes por regulación (Reg G, etc.).
- **Herramientas de precisión:** calculadora de daño determinista, análisis de cobertura de tipos, validación de equipos según reglas oficiales.
- **Inteligencia artificial:** un coach que entiende el contexto competitivo y ayuda a mejorar equipos y decisiones.
- **Experiencia premium:** una interfaz al nivel de un producto esports profesional — rápida, clara, orientada a datos, y bella.

La sensación que buscamos: **"el centro de mando de un jugador competitivo"**. Precisión, estrategia, datos y tecnología.

---

## 3. Áreas principales del producto (Main Product Areas)

Estas son las áreas funcionales del producto. **Importante:** hoy casi todas las pantallas del frontend son *placeholders* ("Próximamente") — la funcionalidad real se irá construyendo por fases. Se indica el estado real de cada una.

| Área | Qué es | Estado actual |
|---|---|---|
| **Meta Analysis** | Estadísticas de uso del metajuego: qué Pokémon, objetos y movimientos dominan cada regulación. | Pantalla placeholder (`app/(tabs)/meta.tsx`). Endpoint `/api/v1/meta/usage` existe pero aún sin datos de uso. |
| **Pokémon Explorer** | Buscador/navegador de todos los Pokémon con filtros (tipo, estadísticas, formas). | **[PLANIFICADO]** Sin pantalla propia todavía. El backend YA tiene los datos (más de 5.400 registros importados de Showdown) y el endpoint `/api/v1/pokemon` funciona. |
| **Pokémon Details** | Ficha completa de un Pokémon: estadísticas base, tipos, habilidades, movimientos aprendibles (learnset). | **[PLANIFICADO]** Sin pantalla. Endpoint `/api/v1/pokemon/{id}` YA funciona y devuelve todo, incluido el learnset. |
| **Team Analysis** | Analizador de equipos: debilidades, cobertura, amenazas del meta contra tu equipo. | Pantalla placeholder (`app/analyzer.tsx`). |
| **Team Builder** | Constructor de equipos de 6 Pokémon con validación de reglas VGC. | Pantalla placeholder (`app/team-builder.tsx`). |
| **Team Core Analysis** | Análisis de "cores" (núcleos de 2-3 Pokémon que funcionan juntos en el meta). | **[PLANIFICADO]** Endpoint `/api/v1/cores` existe (vacío por ahora). Sin pantalla. |
| **Type Coverage** | Análisis de cobertura de tipos: qué tipos cubre tu equipo ofensiva y defensivamente. | **[PLANIFICADO]** El backend tiene la tabla de tipos (`/api/v1/types/chart`). Sin pantalla propia (formará parte del Analyzer/Team Builder). |
| **Damage Calculator** | Calculadora de daño determinista estilo VGC (¿cuánto daño hace X a Y?). | Pantalla placeholder (`app/damage-calculator.tsx`). El motor de cálculo backend está reservado pero **no implementado aún**. |
| **Tournament Explorer** | Explorador de torneos oficiales y no oficiales. | Pantalla placeholder (`app/(tabs)/tournaments.tsx`). Endpoint `/api/v1/tournaments` existe (vacío). |
| **Tournament Standings** | Clasificaciones de torneos: posiciones, jugadores, equipos usados. | **[PLANIFICADO]** Endpoint `/api/v1/standings` existe (vacío). Sin pantalla. |
| **Replica Teams** | Equipos "réplica" de jugadores profesionales para estudiar y copiar. | **[FUTURO]** Fuente de datos externa aún no conectada. Endpoint `/api/v1/teams` existe (vacío). |
| **AI Analysis** | Coach de IA (Claude): chat estratégico y análisis automático de equipos. | **Backend YA funciona** (`/api/v1/ai/coach/chat` y `/api/v1/ai/analyze/team`). **No hay UI todavía** — es una gran oportunidad de diseño. |
| **VGC Knowledge / Team Building** | Guía educativa: fundamentos de VGC, formatos, regulaciones, estrategia. | Pantalla placeholder (`app/vgc-guide.tsx`). |

---

## 4. Responsabilidades de Paola

Paola es la **propietaria del diseño** de VGC Intelligence. Esto incluye:

- **UX** — flujos de usuario, arquitectura de información, jerarquía de pantallas.
- **UI** — diseño visual de cada pantalla y componente.
- **Identidad visual** — logo, marca, personalidad visual del producto.
- **Sistema de diseño** — tokens, componentes reutilizables, patrones consistentes.
- **Tipografía** — elección de fuentes, escalas, jerarquías de texto.
- **Sistema de color** — paleta, semántica de colores, modos (oscuro/claro si aplica).
- **Layout** — grids, espaciados, composición responsive.
- **Componentes** — diseño (y rediseño) de cards, botones, listas, tablas de datos, etc.
- **Animaciones** — transiciones de pantalla, feedback visual.
- **Micro-interacciones** — estados de pulsado, loaders, gestos.
- **Diseño responsive** — móvil, tablet, escritorio, pantallas grandes.
- **Accesibilidad** — contraste, tamaños táctiles, etiquetas de accesibilidad.
- **Presentación visual del frontend** — todo lo que el usuario ve y toca.

En resumen: **si el usuario lo ve, es territorio de Paola.**

---

## 5. Lo que Paola NO necesita trabajar

Estas áreas existen en el repositorio pero están **fuera de tu responsabilidad principal**. No necesitas entenderlas en profundidad ni tocarlas:

- **Backend** (`/backend`) — el servidor FastAPI en Python.
- **Base de datos** — MongoDB y sus colecciones (`sd_pokemon`, `sd_moves`, etc.).
- **Ingesta/sincronización de Showdown** (`/backend/ingestion`) — el sistema que importa datos oficiales de Pokémon.
- **Infraestructura de IA** (`/backend/ai_services`) — la integración con Claude.
- **Motores de cálculo** (`/backend/calculation`) — reservado para la futura calculadora de daño.
- **Infraestructura de testing** (`/tests`) — los tests automáticos del backend.
- **Pipelines de datos** — sincronización, importaciones, adaptadores de fuentes externas.

Si un diseño tuyo necesita un dato que el backend no ofrece todavía, **no intentes crearlo tú**: coméntalo con Juan y se planifica.

---

## 6. Arquitectura del frontend

Todo lo siguiente está verificado contra el código real en `/frontend`.

### Framework y tecnologías

- **Expo SDK 54** + **React Native 0.81** + **React 19** — una sola base de código que funciona en **Android, iOS y web** (vía `react-native-web`).
- **TypeScript** en todos los archivos.
- **Expo Router 6** — enrutado basado en archivos (ver abajo).
- Librerías visuales ya instaladas y disponibles: `expo-image` (imágenes optimizadas), `expo-linear-gradient` (degradados), `expo-blur`, `expo-haptics` (vibración táctil), `react-native-reanimated` (animaciones), `react-native-gesture-handler` (gestos), `@expo/vector-icons` (iconos Ionicons).

### Enrutado (routing)

Expo Router usa **enrutado por archivos**: cada archivo dentro de `/frontend/app` es una pantalla, y su ruta es su path.

```
frontend/app/
├── _layout.tsx            → Layout raíz (Stack, splash screen, providers globales)
├── +html.tsx              → Plantilla HTML solo para web
├── (tabs)/                → Grupo de pestañas (navegación principal)
│   ├── _layout.tsx        → Barra de pestañas inferior (4 tabs)
│   ├── index.tsx          → 🏠 Inicio (home con hero, estado, accesos rápidos)
│   ├── meta.tsx           → 📊 Meta (placeholder "Próximamente")
│   ├── tournaments.tsx    → 🏆 Torneos (placeholder)
│   └── menu.tsx           → ☰ Menú (lista de herramientas secundarias)
├── teams.tsx              → Equipos (pantalla secundaria, placeholder)
├── team-builder.tsx       → Team Builder (placeholder)
├── damage-calculator.tsx  → Calculadora de daño (placeholder)
├── analyzer.tsx           → Analizador (placeholder)
└── vgc-guide.tsx          → Guía VGC (placeholder)
```

**Patrón de navegación actual:** 4 pestañas inferiores (Inicio, Meta, Torneos, Menú) + pantallas secundarias que se abren encima con botón "atrás" (patrón stack). Las transiciones usan animación `fade`.

### Código compartido (`frontend/src`)

```
frontend/src/
├── components/
│   ├── ComingSoon.tsx      → Pantalla "Próximamente" (imagen + degradado + CTA)
│   ├── SecondaryScreen.tsx → Pantalla secundaria con barra superior y botón atrás
│   └── LangToggle.tsx      → Botón para alternar idioma ES/EN
├── hooks/
│   └── use-icon-fonts.ts   → Carga de las fuentes de iconos (Ionicons) al arrancar
├── i18n.tsx                → Sistema de traducciones ES/EN (React Context)
├── theme.ts                → Tokens de diseño: colores, espaciado, radios, tipografía
└── utils/storage/          → Almacenamiento local (AsyncStorage/SecureStore, con variante web)
```

### Gestión de estado

- Actualmente **solo React Context** para el idioma (`I18nProvider` en `src/i18n.tsx`). El idioma por defecto es **español**.
- No hay Redux, Zustand ni similar todavía. **[FUTURO]** Se añadirá gestión de estado cuando las pantallas consuman datos reales.

### Sistema de estilos

- **`StyleSheet.create()` de React Native** en cada componente (NO se usa CSS, NO Tailwind, NO styled-components).
- Todos los estilos consumen los **tokens de `src/theme.ts`** (ver sección 9). Nunca hay colores/espaciados "a mano" — siempre `colors.x`, `spacing.x`, `radius.x`, `fontSize.x`.

### Servicios / llamadas a API

- **No existe todavía una capa de servicios** (no hay `src/services/` ni cliente API). Las pantallas actuales son placeholders y no llaman al backend.
- **[PLANIFICADO]** Cuando las pantallas consuman datos, se creará un cliente API que use la variable de entorno `EXPO_PUBLIC_BACKEND_URL` (ya definida en `frontend/.env` — **nunca modificar ese archivo**).

### Assets existentes

```
frontend/assets/
├── fonts/SpaceMono-Regular.ttf        → Fuente monoespaciada (de la plantilla, no se usa activamente)
└── images/
    ├── icon.png, adaptive-icon.png    → Iconos de la app (placeholder)
    ├── splash-image.png, app-image.png→ Splash screen (placeholder)
    ├── favicon.png                    → Favicon web (placeholder)
    └── react-logo*.png, partial-react-logo.png → Restos de la plantilla Expo
```

Las imágenes de fondo del hero y de las pantallas "Próximamente" son **URLs de Unsplash** embebidas en el código (no assets locales) — pensadas como temporales.

### Archivos relacionados con diseño

- `frontend/src/theme.ts` — tokens de diseño actuales.
- `/app/design_guidelines.json` (raíz del repo) — las guías generadas para el placeholder actual. **Referencia, no ley:** tú defines la identidad final.
- `frontend/app.json` — configuración de Expo (nombre, iconos, splash).

### ⚠️ Archivos que NUNCA debes modificar

- `frontend/.env` — URLs de entorno (romperlas rompe la preview).
- `frontend/metro.config.js` — configuración del bundler.
- `frontend/package.json` — dependencias (si necesitas una librería nueva, pídesela a Juan; se instala con `yarn expo install`).

---

## 7. Frontera Backend/API (cómo el frontend obtiene datos)

### Explicación sencilla

El backend es un servidor que guarda todos los datos (Pokémon, movimientos, torneos…) en una base de datos. El frontend **no accede a la base de datos directamente**: le pide los datos al backend a través de **endpoints** — URLs que devuelven datos en formato JSON.

Ejemplo real: si el frontend pide `GET /api/v1/pokemon?q=incineroar`, el backend responde con un JSON con los datos de Incineroar. El frontend solo tiene que "pintar" ese JSON.

**Regla de oro para Paola:** puedes cambiar TODO lo visual libremente, pero los nombres de los endpoints y la forma de sus datos (el "contrato de la API") los define el backend. Si necesitas un dato nuevo, se pide, no se inventa.

### Endpoints existentes relevantes para el frontend

Todos empiezan por `/api/v1/`. Los marcados ✅ ya devuelven datos reales; los marcados ⬜ existen pero devuelven listas vacías hasta futuras fases.

**Salud del sistema**
- ✅ `GET /api/v1/health` — comprueba que el backend está vivo.
- ✅ `GET /api/v1/health/db` — comprueba la base de datos.

**Datos canónicos de Pokémon (importados de Showdown — ¡con datos reales!)**
- ✅ `GET /api/v1/pokemon` — lista paginada. Parámetros: `limit`, `offset`, `only_base` (solo especies base), `q` (búsqueda por nombre).
- ✅ `GET /api/v1/pokemon/{id}` — ficha completa de un Pokémon (por nombre o número), incluye learnset.
- ✅ `GET /api/v1/moves` — lista de movimientos.
- ✅ `GET /api/v1/abilities` — habilidades.
- ✅ `GET /api/v1/items` — objetos.
- ✅ `GET /api/v1/natures` — naturalezas.
- ✅ `GET /api/v1/types` — tipos.
- ✅ `GET /api/v1/types/chart` — tabla de efectividad de tipos (clave para Type Coverage).
- ✅ `GET /api/v1/formats` — formatos de juego (VGC Reg G, etc.).
- ✅ `GET /api/v1/rulesets` — conjuntos de reglas.
- ✅ `GET /api/v1/regulations` — regulaciones VGC.

**Datos competitivos (estructuras listas, datos en fases futuras)**
- ⬜ `GET /api/v1/meta/usage` — estadísticas de uso del meta.
- ⬜ `GET /api/v1/cores` — núcleos de equipos.
- ⬜ `GET /api/v1/teams` — equipos.
- ⬜ `GET /api/v1/tournaments` — torneos.
- ⬜ `GET /api/v1/standings` — clasificaciones.
- ⬜ `GET /api/v1/sources` — fuentes de datos conectadas.

**Inteligencia artificial (¡ya funcionan!)**
- ✅ `POST /api/v1/ai/coach/chat` — chat con el coach IA (respuesta en streaming, palabra a palabra, como ChatGPT).
- ✅ `POST /api/v1/ai/analyze/team` — análisis automático de un equipo.
- ✅ `DELETE /api/v1/ai/coach/chat/{session_id}` — borra una conversación.

**Administración (NO son para la UI de usuario)**
- `GET/POST /api/v1/admin/showdown/*` — sincronización de datos; requieren token de administrador. No diseñar UI pública para esto.

---

## 8. Componentes existentes

Antes de crear componentes nuevos, conoce (y considera reutilizar o evolucionar) los que ya existen:

| Componente | Archivo | Qué hace |
|---|---|---|
| **`ComingSoon`** | `src/components/ComingSoon.tsx` | Pantalla "Próximamente": imagen de fondo, degradado oscuro, badge con punto pulsante, título, texto y botón "Volver al inicio". Es el placeholder de casi todas las secciones. |
| **`SecondaryScreen`** | `src/components/SecondaryScreen.tsx` | Envoltorio para pantallas secundarias: barra superior con botón atrás + título centrado, y un `ComingSoon` dentro. |
| **`LangToggle`** | `src/components/LangToggle.tsx` | Píldora con icono de globo que alterna el idioma ES ↔ EN. Aparece en las cabeceras. |

Además, hay **patrones visuales repetidos dentro de las pantallas** (definidos inline en `app/(tabs)/index.tsx` y `menu.tsx`) que son candidatos naturales a convertirse en componentes del sistema de diseño:

- **Tarjeta/tile de acceso rápido** (grid 2 columnas en Home): icono en caja, título, descripción, footer con etiqueta "PRÓXIMAMENTE".
- **Fila de menú** (lista en Menú): icono + título + descripción + chevron.
- **StatusPill** (Home): píldora de estado con punto de color (verde = activo).
- **Hero con imagen + degradado + tag** (Home).
- **Badge/tag de regulación** ("VGC · REG G").

Todo lo demás son componentes nativos de React Native (`View`, `Text`, `Pressable`, `ScrollView`) e iconos **Ionicons** de `@expo/vector-icons`.

---

## 9. Sistema de diseño

### Lo que existe hoy (tokens en `src/theme.ts`)

El placeholder actual usa un tema **oscuro estilo esports** con estos tokens:

- **Colores:** superficie casi negra (`#0B0E14`), superficies secundarias/terciarias grises azuladas, marca índigo/violeta (`#4F46E5` / `#6366F1` / `#8B5CF6`), y semánticos (éxito verde, aviso ámbar, error rojo, info azul).
- **Espaciado:** escala de 4 a 48 px (`xs`=4, `sm`=8, `md`=12, `lg`=16, `xl`=24, `xxl`=32, `xxxl`=48).
- **Radios:** 6 / 12 / 20 / pill (999).
- **Tipografía:** tamaños de 12 a 28. Actualmente usa la fuente del **sistema** (no hay fuente de marca cargada).

### Lo importante: la identidad visual está ABIERTA

El tema actual es un **placeholder funcional**, no una decisión final. **Tú tienes libertad total para definir la identidad visual** de VGC Intelligence. No hay una paleta ni un estilo prescritos.

Se te anima a explorar un lenguaje visual distintivo y apropiado para:

- **Pokémon VGC competitivo** — con personalidad, pero profesional (evitar estética infantil).
- **Esports** — energía, intensidad, broadcast-quality.
- **Análisis de datos** — legibilidad de tablas, gráficas y números por encima de todo.
- **Estrategia** — sensación de control, planificación, inteligencia.
- **Precisión** — detalle, exactitud, confianza en los datos.
- **Tecnología** — moderno, rápido, pulido.

Consejo práctico: la vía de menor fricción es **evolucionar los tokens en `theme.ts`** (todos los componentes ya los consumen), y desde ahí rediseñar componentes y pantallas.

---

## 10. Diseño responsive

La aplicación debe funcionar bien en:

- **Android/móvil** — la prioridad #1. Diseño *mobile-first*, uso con una mano, pulgar como cursor.
- **Tablets** — aprovechar el espacio: más columnas, paneles laterales.
- **Escritorio (web)** — experiencia fuerte: layouts anchos, tablas de datos completas, hover states.
- **Pantallas grandes** — limitar anchos máximos de contenido para no "estirar" la UI.

Reglas prácticas ya vigentes en el código:

- Áreas táctiles mínimas de **44×44 px**.
- Respetar los *safe areas* (notch, barra de gestos) — ya se usa `react-native-safe-area-context`.
- Grid de espaciado basado en la escala de `theme.ts`.
- La misma base de código sirve móvil y web: piensa cada pantalla en ambos contextos.

---

## 11. Principios de animación

Las animaciones deben **comunicar, no decorar**. En una app de datos competitivos, el contenido manda:

- **Estado:** loaders, éxito/error, sincronización de datos.
- **Jerarquía:** qué elemento acaba de aparecer o cambiar (p. ej., resaltar una fila nueva en una tabla).
- **Interacción:** feedback inmediato al pulsar (los `Pressable` actuales ya bajan opacidad/cambian borde).
- **Transiciones:** continuidad entre pantallas (el stack actual usa `fade`).

Evitar: animaciones largas, rebotes exagerados, movimiento constante que distraiga de leer datos. Preferir transiciones de 150–300 ms.

Herramientas disponibles: `react-native-reanimated` (ya instalada, motor de animación de alto rendimiento), `expo-haptics` (vibración sutil en acciones clave), `expo-image` (transiciones de carga de imagen, ya se usa con `transition={200}`).

---

## 12. Propiedad de los assets

- Los assets actuales (`frontend/assets/`) son **placeholders de plantilla** (iconos genéricos, logos de React, imágenes de Unsplash embebidas). Puedes y debes reemplazarlos como parte del trabajo de identidad visual.
- **Los assets que cree Paola** (logos, iconografía, ilustraciones, fuentes, imágenes de marca) son **propiedad del diseño**: nadie debe **eliminarlos, reemplazarlos, renombrarlos ni modificarlos sustancialmente** sin coordinarlo explícitamente con Paola.
- Recomendación: mantener los assets de diseño dentro de `frontend/assets/` con nombres claros y, si crece, subcarpetas (`brand/`, `illustrations/`, etc.).
- La misma regla aplica en sentido inverso: no borrar assets existentes que otras partes del código usen sin verificarlo antes (ver sección 17).

---

## 13. Flujo de trabajo con Git

Reglas del repositorio (acordadas con Juan):

- **`main`** = rama estable, fuente de verdad. **Nadie trabaja directamente sobre `main`.** Solo recibe cambios mediante Pull Requests revisados.
- **`frontend/paola`** = **tu rama de trabajo**. Todo tu trabajo vive aquí.
- (Contexto: existe también `emergent/development`, la rama del agente de desarrollo. No la uses.)

### Ciclo de trabajo de Paola

1. **Antes de empezar trabajo importante:** actualiza tu rama con lo último de `main`:
   ```bash
   git checkout frontend/paola
   git pull origin main
   ```
2. **Trabaja y haz commits** con mensajes claros:
   ```bash
   git add .
   git commit -m "design: nueva paleta de colores y tokens tipográficos"
   ```
3. **Sube tus cambios a tu rama:**
   ```bash
   git push origin frontend/paola
   ```
4. **Crea un Pull Request** de `frontend/paola` → `main` en GitHub.
5. **Juan revisa** el PR y lo fusiona a `main`.

⛔ **Paola nunca trabaja directamente sobre `main`.** Ni commits ni pushes a `main`, jamás.

---

## 14. Roadmap de diseño (sugerido)

Un orden de trabajo propuesto — ajustable según prioridades con Juan:

### Fase A — Fundación
- Exploración de identidad visual: logo, paleta, tipografía, tono.
- Sistema de diseño v1: rediseñar los tokens de `theme.ts`, definir componentes base (botones, cards, píldoras, inputs, tablas de datos, estados vacíos/carga/error).
- Rediseño de las pantallas existentes: Home, Menú, barra de pestañas, pantalla "Próximamente".
- Assets de marca: icono de app, splash screen, favicon.

### Fase B — Pokémon Explorer
- Diseño del buscador/listado de Pokémon (el backend ya tiene los datos).
- Ficha de detalle de Pokémon: estadísticas base (visualización de stats), tipos, habilidades, learnset.
- Patrones clave: chips de tipo con color, barras de estadísticas, listas largas con búsqueda y filtros.

### Fase C — Meta Analysis
- Dashboards de uso del metajuego: rankings, porcentajes, tendencias.
- Visualización de datos: gráficas, tablas comparativas, indicadores de subida/bajada.
- Vistas por regulación/formato.

### Fase D — Team Builder
- Flujo de construcción de un equipo de 6: selección de Pokémon, movimientos, objetos, habilidades, EVs/naturaleza.
- Vista resumen del equipo y validación visual de reglas.
- Integración del análisis de cobertura de tipos.

### Fase E — Battle Tools
- Calculadora de daño: entrada de atacante/defensor, resultado con rangos, escenarios.
- Analizador de equipos y amenazas.
- UI del coach de IA: chat en streaming + presentación del análisis de equipo (el backend ya está listo).

### Fase F — Tournament Explorer
- Listado y detalle de torneos, clasificaciones (standings), equipos réplica de jugadores profesionales.

---

## 15. Filosofía de placeholders

Durante el desarrollo, el equipo crea **placeholders funcionales**: pantallas y componentes que funcionan (navegan, muestran estructura) pero cuyo aspecto es provisional.

- Los placeholders existen para **desbloquear el desarrollo**, no para definir el diseño.
- Paola puede **rediseñarlos por completo** más adelante **sin cambiar la funcionalidad subyacente** (navegación, testIDs, llamadas a datos).
- Es el patrón esperado del proyecto: primero funciona, luego se embellece — y ambas cosas pueden evolucionar en paralelo gracias a la separación por ramas.

---

## 16. Libertad de diseño

Que quede claro: **no estás obligada a conservar nada del estilo placeholder actual.**

- La paleta índigo/violeta, las imágenes de Unsplash, la tipografía del sistema, el estilo de las cards — todo es provisional y reemplazable.
- Se te anima activamente a crear una **identidad visual única** para VGC Intelligence, con la ambición de un producto esports profesional.
- Los únicos límites reales son los técnicos y funcionales de la sección 17.

---

## 17. Reglas importantes de desarrollo

1. **Preservar la funcionalidad existente.** Un rediseño no debe romper la navegación, el cambio de idioma ni ninguna interacción que ya funcione. Prueba la app después de cada cambio.
2. **Reutilizar componentes cuando sea posible.** Antes de crear un componente nuevo, revisa `src/components/` y los patrones de la sección 8.
3. **Evitar duplicación innecesaria.** Si el mismo estilo aparece en 3 sitios, probablemente debería ser un token o un componente compartido.
4. **No romper los contratos de la API.** No cambies nombres de endpoints ni la forma esperada de los datos. Lo visual es tuyo; los datos son del backend.
5. **No eliminar assets existentes** sin verificar que nada los usa (buscar el nombre del archivo en el código) y sin avisar.
6. **Comunicar antes de cambiar funcionalidad compartida.** Cambios en `theme.ts`, `i18n.tsx`, layouts (`_layout.tsx`) o componentes compartidos afectan a toda la app — coordínalos con Juan.
7. **Separar lo visual de lo funcional cuando sea práctico.** Idealmente, tus commits cambian estilos, layouts y assets; si necesitas tocar lógica, coméntalo primero.
8. **Mantener los `testID`.** Los elementos tienen atributos `testID` (p. ej. `testID="home-hero"`) que usan los tests automáticos. Al rediseñar, consérvalos.
9. **Textos siempre vía i18n.** Nunca escribas textos "a mano" en las pantallas: añade la clave en `src/i18n.tsx` (en ES y EN) y úsala con `t('clave')`.
10. **No tocar los archivos protegidos:** `frontend/.env`, `frontend/metro.config.js`, `frontend/package.json` (dependencias vía Juan).

---

## 18. Inicio rápido para Paola

- [ ] 1. **Clona el repositorio** desde GitHub.
- [ ] 2. **Cambia a tu rama:** `git checkout frontend/paola` (y `git pull origin main` para estar al día).
- [ ] 3. **Lee esta guía** completa (ya casi está ✔).
- [ ] 4. **Inspecciona el frontend existente:** `frontend/app/` (pantallas), `frontend/src/` (componentes, tema, i18n).
- [ ] 5. **Ejecuta la aplicación:** dentro de `frontend/`, instala dependencias con `yarn` y arranca con `yarn start` (Expo te dará opciones para web, Android e iOS).
- [ ] 6. **Explora las pantallas existentes:** Home, Meta, Torneos, Menú y las secundarias (Equipos, Team Builder, Calculadora, Analizador, Guía VGC). Prueba el toggle ES/EN.
- [ ] 7. **Revisa la documentación de la API:** con el backend corriendo, abre `/docs` (Swagger interactivo de FastAPI) para ver todos los endpoints y probar respuestas reales; complemento: sección 7 de esta guía y `/documentation/DATA_SOURCES.md`.
- [ ] 8. **Empieza la exploración del sistema de diseño:** identidad, paleta, tipografía, tokens (Fase A del roadmap).
- [ ] 9. **Haz commits** frecuentes y descriptivos.
- [ ] 10. **Sube a tu rama:** `git push origin frontend/paola`.
- [ ] 11. **Crea un Pull Request** hacia `main` y espera la revisión de Juan.

---

**¿Dudas?** Pregunta a Juan. Bienvenida al equipo, Paola — este producto va a lucir tan bien como tú lo diseñes. 🎨
