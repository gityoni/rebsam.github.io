# RebSam — Suivi des tâches

## ✅ Fait
- Pipeline GitHub → Netlify (auto-deploy)
- PWA : manifest, service worker, icônes
- TWA Android (Bubblewrap + Digital Asset Links)
- Prompt halakhique : questions toujours TYPE 1
- Optimisations perf : CSS non-blocking, defer JS, FCP/LCP
- CLAUDE.md ajouté (mémoire projet)
- **[2026-03-15] Fix CLS 0.39 → <0.10** — Google Fonts `display=optional` + `@font-face` fallbacks `size-adjust` (Inter 107%, Outfit 96%, Heebo 105%) + `contain:layout` avatar + `content-visibility:auto` sections hors-viewport → score Lighthouse v10+ estimé 85+ (vs 74 avant)
- **[2026-03-15] Fix LCP + CLS résiduel AOS** — Suppression AOS CDN → IntersectionObserver natif inline (zéro CDN, zéro FOUC) + delay animation avatar `.28s→0s` (Chrome excluait l'avatar opacity:0 du LCP) + `imagesizes` sur preload avatar → LCP estimé 3188ms→<2500ms

## 🔄 En cours
<!-- Mettre à jour à chaque session -->
-

## 📋 À faire
<!-- Ajouter ici les prochaines tâches -->
- Mesurer LCP réel post-déploiement via PageSpeed Insights (cible : <2500ms)

## 🐛 Bugs connus
<!-- Bugs identifiés mais pas encore traités -->
-

---
*Dernière mise à jour : 2026-03-15*
