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
- **[2026-03-24] Boost profiles recalibrés** — Répartition réelle corpus analysée (1972 docs). Niveau 3 (141 docs Sifrey Halacha) = moteur halacha principal → boost 0.8. Niveau 2 (29 docs Responsa) → 0.7. Niveau 4 kabbalah/Breslav écarté des questions pratiques (-0.2). Commentaires de répartition ajoutés dans le code.
- **[2026-03-24] Fix UI chat** — Fond `#chat-box` saumon → `#f8fafc` neutre. Zone input `#fef5f0` → `#f0f4fb` bleuté. Header gradient harmonisé bleu→violet→corail (design system).
- **[2026-03-25] Streaming SSE** — Frontend migré vers `/stream` (SSE). Texte affiché token par token. Latence perçue ~1s vs ~10s avant.
- **[2026-03-25] Migration Cloudflare Pages** — Netlify → Cloudflare Pages. `_redirects` + `_headers` créés. DNS rebsam.fr → Cloudflare. Netlify désactivé (conservé rollback).

## 🔄 En cours

- 12 testeurs Play Store test fermé → compteur 14 jours en cours

## 🔴 PRIORITÉ

### 1. IARC Rating ID réel
- Google Play Console → ton app → Contenu de l'app → Classification du contenu
- Remplir le questionnaire IARC → copier l'ID généré
- Remplacer le placeholder dans `manifest.json` et committer

### 3. Hiérarchie des sources dans `proxy/prompt.txt`
**Statut :** partiellement traité via boost profiles (Vertex AI remonte les bonnes sources).
Le problème résiduel est dans l'**ordre d'affichage dans la réponse** (pas la recherche).

**Fix restant dans la section `📖 SOURCES PRÉCISES`** :
```
ORDRE OBLIGATOIRE DES SOURCES (du plus primaire au plus récent) :
1. Talmud Bavli / Yerushalmi, Rambam (Michné Torah), Tur
2. Shulchan Aruch (Maran) + Rama, Beit Yossef, Darchei Moshe
3. Acharonim classiques : Mishna Beroura, Ben Ich Haï, Kaf HaHaïm, Aruch HaShulchan
4. Poskim contemporains : Yalkout Yossef, Igrot Moshe, Tzitz Eliezer, Chevet Daat...
5. Ouvrages thématiques modernes EN DERNIER
INTERDIT : citer un ouvrage thématique moderne si une source primaire couvre le même point.
```

## 📋 À faire (suite)

- Affiner les boosts par sous-catégorie : ajouter champ `source_category` dans métadonnées Vertex AI (ex. "Sifrey Halacha" distingué de "Parashat Shavua" dans profil halakha)
- Soumettre l'AAB sur Google Play Console (test interne d'abord)
- Mesurer LCP réel post-déploiement via PageSpeed Insights (cible : <2500ms)
- Invalider le cache og-image sur Facebook Sharing Debugger après merge → main
- Vérifier rendu thumbnail Telegram/WhatsApp avec la nouvelle og-image
- Supprimer l'ancienne trigger Buildpack GCP (échoue sur GOOGLE_FUNCTION_SOURCE)

## 🐛 Bugs connus

- **Ordre d'affichage sources dans la réponse** : boost profiles corrigent la recherche, mais l'ordre de citation dans le texte reste à fixer dans prompt.txt
- **IARC rating** : placeholder dans manifest.json, à remplacer par ID réel

---
*Dernière mise à jour : 2026-03-25*
