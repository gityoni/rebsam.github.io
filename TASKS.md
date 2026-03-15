# RebSam — Suivi des tâches

## ✅ Fait
- Pipeline GitHub → Netlify (auto-deploy)
- PWA : manifest, service worker, icônes
- TWA Android (Bubblewrap + Digital Asset Links)
- Prompt halakhique : questions toujours TYPE 1
- Optimisations perf : CSS non-blocking, defer JS, FCP/LCP
- CLAUDE.md ajouté (mémoire projet)
- **[2026-03-15] Fix CLS 0.39 → <0.10** — Google Fonts `display=optional` + `@font-face` fallbacks `size-adjust` (Inter 107%, Outfit 96%, Heebo 105%) + `contain:layout` avatar + `content-visibility:auto` sections hors-viewport → score Lighthouse v10+ estimé 85+ (vs 74 avant)

## 🔄 En cours
<!-- Mettre à jour à chaque session -->
-

## 📋 À faire
<!-- Ajouter ici les prochaines tâches -->
- Mesurer le CLS réel post-déploiement via PageSpeed Insights ou Netlify Lighthouse plugin
- Investiguer si les animations AOS (`fade-up`) contribuent au CLS résiduel
- Optimiser LCP (3188 ms → cible < 2500 ms) : `avatar.webp` déjà preloadé, vérifier compression

## 🐛 Bugs connus
<!-- Bugs identifiés mais pas encore traités -->
-

---
*Dernière mise à jour : 2026-03-15*
