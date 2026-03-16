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
- **[2026-03-15] Refonte og-image.png** — Recomposition bannière OG : même logo/couleurs/avatar, layout propre colonne gauche texte / droite avatar, sans débordement → meilleur rendu thumbnail Telegram/Facebook/WhatsApp
- **[2026-03-16] Fix build Android AAB — broken pipe sdkmanager** — `yes | sdkmanager --licenses` avec `set -euo pipefail` → broken pipe exit 141 → fix `(yes 2>/dev/null || true) | sdkmanager --licenses`
- **[2026-03-16] Fix build Android AAB — androidSdk isn't correct** — Bubblewrap validait le SDK via `ANDROID_HOME` (non défini) en plus de `config.json` → remplacement de l'installation manuelle par `android-actions/setup-android@v3` qui expose correctement `ANDROID_HOME` + `ANDROID_SDK_ROOT`

## 🔄 En cours
<!-- Mettre à jour à chaque session -->
- Build AAB Android à valider (dernier fix poussé, pas encore retesté)

## 📋 À faire
<!-- Ajouter ici les prochaines tâches -->
- Mesurer LCP réel post-déploiement via PageSpeed Insights (cible : <2500ms)
- Invalider le cache og-image sur Facebook Sharing Debugger après merge → main
- Vérifier rendu thumbnail Telegram/WhatsApp avec la nouvelle og-image

## 🐛 Bugs connus
<!-- Bugs identifiés mais pas encore traités -->
-

---
*Dernière mise à jour : 2026-03-16 (session soir)*
