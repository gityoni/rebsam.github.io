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
- **[2026-03-18] Cloud Run auto-deploy confirmé** — Cloud Build déclenché automatiquement sur push main, révision 00049-bnm déployée instantanément
- **[2026-03-20] Fix routing Claude + trafic Cloud Run** — Erreur 404 Vertex AI (endpoint Gemini appelé avec modèle Claude) → code `USE_CLAUDE` déployé sur révision 00063-j52 + trafic basculé vers dernière révision. Ancienne trigger Buildpack à supprimer (échoue sur GOOGLE_FUNCTION_SOURCE).
- **[2026-03-18] Prompt : règle FLUIDITÉ & HUMANITÉ** — Transitions naturelles entre sections, variété des formules d'entrée, interdiction de commencer par un titre en gras, utilisation du prénom utilisateur
- **[2026-03-22] Sources + emoji (branche, pas encore sur main)** — Règle prompt sources (français d'abord, hébreu entre parenthèses), post-processing Python `_fix_hebrew_first_sources`, emoji `📜→⚖️`, anti-anglicismes (leniency→tolérance etc.)

## 🔄 En cours
- PR `claude/update-claude-docs-WytQh` → main : à merger pour déployer les fixes sources/emoji

## 🔴 PRIORITÉ — À faire demain

### 1. Merger la branche → main (pour activer les fixes déjà codés)
- `git checkout main && git merge claude/update-claude-docs-WytQh && git push`
- → déclenche Cloud Run deploy automatique
- Tester en prod : les sources doivent commencer par le nom français

### 2. Hiérarchie des sources — sources secondaires citées avant les primaires
**Problème observé :** le modèle cite en premier des ouvrages modernes/thématiques (`נשים בהלכה`, `שמירת עיניים כהלכה`) au lieu des sources primaires halakhiques.

**Fix à faire dans `proxy/prompt.txt`** — ajouter dans la section `📖 SOURCES PRÉCISES` :
```
ORDRE OBLIGATOIRE DES SOURCES (du plus primaire au plus récent) :
1. Talmud Bavli / Yerushalmi, Rambam (Michné Torah), Tur
2. Shulchan Aruch (Maran) + Rama, Beit Yossef, Darchei Moshe
3. Acharonim classiques : Mishna Beroura, Ben Ich Haï, Kaf HaHaïm, Aruch HaShulchan
4. Poskim contemporains : Yalkout Yossef, Igrot Moshe, Tzitz Eliezer, Chaövet Daät...
5. Ouvrages thématiques modernes EN DERNIER (Shmirat Einayim, Nashim BaHalachah...)
INTERDIT : citer un ouvrage thématique moderne si une source primaire couvre le même point.
```

**Résultat attendu :**
- Avant : `- נשים בהלכה, סעיף כ : aliment Parev...`
- Après : `- Shulchan Aruch, Yoreh Deah, Siman 95 : aliment Parev...`

## 📋 À faire (suite)
- Soumettre l'AAB sur Google Play Console (test interne d'abord)
- Mesurer LCP réel post-déploiement via PageSpeed Insights (cible : <2500ms)
- Invalider le cache og-image sur Facebook Sharing Debugger après merge → main
- Vérifier rendu thumbnail Telegram/WhatsApp avec la nouvelle og-image

## 🐛 Bugs connus
- **Sources hébreu-first** : fix codé sur branche, pas encore déployé (merge requis)
- **Sources secondaires avant primaires** : règle manquante dans le prompt (à faire demain)

---
*Dernière mise à jour : 2026-03-22*
