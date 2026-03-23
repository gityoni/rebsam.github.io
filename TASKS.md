# RebSam — Suivi des tâches

## ✅ Fait

- Pipeline GitHub → Netlify (auto-deploy)
- PWA : manifest, service worker, icônes
- TWA Android (Bubblewrap + Digital Asset Links)
- Prompt halakhique : questions toujours TYPE 1
- Optimisations perf : CSS non-blocking, defer JS, FCP/LCP
- CLAUDE.md ajouté (mémoire projet)
- **[2026-03-15] Fix CLS 0.39 → <0.10** — Google Fonts `display=optional` + `@font-face` fallbacks `size-adjust` + `contain:layout` avatar + `content-visibility:auto` sections hors-viewport
- **[2026-03-15] Fix LCP + CLS résiduel AOS** — Suppression AOS CDN → IntersectionObserver natif inline + delay animation avatar + `imagesizes` sur preload avatar
- **[2026-03-15] Refonte og-image.png** — Layout propre colonne gauche texte / droite avatar
- **[2026-03-16] Fix build Android AAB — broken pipe sdkmanager**
- **[2026-03-17] Build AAB Android validé** — Pipeline GitHub Actions complet, build #17 Success 4m56s
- **[2026-03-18] Cloud Run auto-deploy confirmé** — Cloud Build déclenché automatiquement sur push main
- **[2026-03-20] Fix routing Claude + trafic Cloud Run** — Erreur 404 Vertex AI corrigée, révision 00063-j52
- **[2026-03-18] Prompt : règle FLUIDITÉ & HUMANITÉ** — Transitions naturelles, variété formules d'entrée
- **[2026-03-22] Sources + emoji** — Règle prompt sources (français d'abord), post-processing `_fix_hebrew_first_sources`, emoji `📜→⚖️`, anti-anglicismes
- **[2026-03-23] PWA manifest complet** — `id`, `screenshots` (mobile 1170×2526 + wide 997×900), `display_override`, `related_applications` (Play Store), `iarc_rating_id` placeholder

## 🔄 En cours

- Branche `claude/update-claude-docs-WytQh` → à merger sur `main`

## 🔴 PRIORITÉ

### 1. Merger la branche → main
- `git checkout main && git merge claude/update-claude-docs-WytQh && git push`
- Déclenche Cloud Run deploy automatique
- Re-tester PWABuilder après deploy (score attendu > 30/45)

### 2. IARC Rating ID réel
- Google Play Console → ton app → Contenu de l'app → Classification du contenu
- Remplir le questionnaire IARC → copier l'ID généré
- Remplacer le placeholder dans `manifest.json` et committer

### 3. Hiérarchie des sources dans `proxy/prompt.txt`
**Problème :** le modèle cite des ouvrages modernes/thématiques avant les sources primaires.

**Fix à faire dans la section `📖 SOURCES PRÉCISES`** :
```
ORDRE OBLIGATOIRE DES SOURCES (du plus primaire au plus récent) :
1. Talmud Bavli / Yerushalmi, Rambam (Michné Torah), Tur
2. Shulchan Aruch (Maran) + Rama, Beit Yossef, Darchei Moshe
3. Acharonim classiques : Mishna Beroura, Ben Ich Haï, Kaf HaHaïm, Aruch HaShulchan
4. Poskim contemporains : Yalkout Yossef, Igrot Moshe, Tzitz Eliezer, Chaövet Daät...
5. Ouvrages thématiques modernes EN DERNIER (Shmirat Einayim, Nashim BaHalachah...)
INTERDIT : citer un ouvrage thématique moderne si une source primaire couvre le même point.
```

## 📋 À faire (suite)

- Soumettre l'AAB sur Google Play Console (test interne d'abord)
- Mesurer LCP réel post-déploiement via PageSpeed Insights (cible : <2500ms)
- Invalider le cache og-image sur Facebook Sharing Debugger après merge → main
- Vérifier rendu thumbnail Telegram/WhatsApp avec la nouvelle og-image
- Supprimer l'ancienne trigger Buildpack GCP (échoue sur GOOGLE_FUNCTION_SOURCE)

## 🐛 Bugs connus

- **Sources secondaires avant primaires** : règle manquante dans le prompt (fix décrit ci-dessus)
- **IARC rating** : placeholder dans manifest.json, à remplacer par ID réel

---
*Dernière mise à jour : 2026-03-23*
