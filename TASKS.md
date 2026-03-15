# TASKS.md — Suivi des tâches RebSam

## Tâches complétées

### [2026-03-15] Fix CLS — Lighthouse performance (v10/v11/v12)
**Problème :** Score Lighthouse Performance mobile 74/100 (v10+) vs 81/100 (v8/v9)
**Cause :** CLS = 0.39 (cible < 0.10) — Google Fonts `display=swap` causait un reflow massif au chargement + poids CLS passé de 15% à 25% en v10

**Fixes apportés dans `index.html` :**
- Google Fonts : `display=swap` → `display=optional` (supprime tout swap de police = zéro CLS fonts)
- Ajout de `@font-face` fallbacks avec `size-adjust` : `Inter-fallback` (107%), `Outfit-fallback` (96%), `Heebo-fallback` (105%) pour minimiser le reflow visuel quand les polices chargent depuis le cache
- `font-family` de `body`, `.logo`, RTL mis à jour avec les fallbacks explicites
- `contain: layout` sur `.hero-avatar-img` pour isoler les repaints
- `content-visibility: auto` + `contain-intrinsic-size` sur les sections hors-viewport (`#how-it-works`, `#pillars`, `#sources`, `#faq`)

**Score estimé après fix :** CLS `0.39 → <0.10` — Lighthouse v10+ : **85+** (vs 74 avant)

---

## Tâches en cours

_(aucune)_

---

## Backlog

- Mesurer le CLS réel post-déploiement via PageSpeed Insights ou Netlify Lighthouse plugin
- Investiguer si les animations AOS (`fade-up`) contribuent au CLS résiduel
- Optimiser LCP (3188 ms → cible < 2500 ms) : `avatar.webp` déjà preloadé, vérifier compression
