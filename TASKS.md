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
- **[2026-03-17] Build AAB Android validé** — Pipeline GitHub Actions complet : fix minSdkVersion 19→21 (androidbrowserhelper:2.6.2), fix cache Gradle (hashFiles sur fichiers inexistants), fix prompts bubblewrap build/update, retries exponentiels 5 tentatives → build #17 Success 4m56s, 2 artifacts générés

## 🔄 En cours
<!-- Mettre à jour à chaque session -->
- Vérification LCP réel + og-image thumbnails

## 📋 À faire
<!-- Ajouter ici les prochaines tâches -->
- **[Cloud Run] Connecter GitHub auto-deploy** — Cloud Run → Edit & Deploy New Revision → Continuously deploy from a repository → repo `gityoni/rebsam.github.io` → branch `^main$` → Dockerfile `/proxy/Dockerfile` → les variables d'env persistent d'une révision à l'autre
- Soumettre l'AAB sur Google Play Console (test interne d'abord)
- Mesurer LCP réel post-déploiement via PageSpeed Insights (cible : <2500ms)
- Invalider le cache og-image sur Facebook Sharing Debugger après merge → main
- Vérifier rendu thumbnail Telegram/WhatsApp avec la nouvelle og-image

## 🐛 Bugs connus
<!-- Bugs identifiés mais pas encore traités -->
-

---
*Dernière mise à jour : 2026-03-17*

