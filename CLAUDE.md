# RebSam — Mémoire projet (Claude Code)

## Identité du projet
Reb Sam est un expert rabbinique augmenté — système expert qui navigue dans les textes sacrés pour fournir des réponses précises, sourcées et adaptées à la tradition. Répond en hébreu, français et anglais.

## Stack technique
- **Frontend** : HTML / JS vanilla (index.html, index.js)
- **PWA** : manifest.json, sw.js (service worker), icon-192.png, icon-512.png
- **Proxy** : dossier `proxy/` (Cloud Run)
- **Android TWA** : twa-manifest.json, .well-known/
- **Déploiement** : Netlify (auto-deploy sur push main)
- **Repo** : gityoni/rebsam.github.io (branche `main`)
- **URL prod** : rebsam.fr
- **Netlify project** : rebsam

## Fichiers clés
| Fichier | Rôle |
|---|---|
| `index.html` | Page principale |
| `index.js` | Logique frontend |
| `sw.js` | Service Worker (cache, network-first) |
| `manifest.json` | Config PWA |
| `netlify.toml` | Config Netlify |
| `proxy/` | Backend proxy (Cloud Run) |
| `admin.html` | Interface admin (webhook Make.com) |

## Workflow de déploiement
```
modifier fichiers
→ git add . && git commit -m "description" && git push
→ Netlify auto-deploy déclenché sur branche main  (frontend)
→ Cloud Run auto-deploy déclenché sur branche main (proxy) ✅ CONFIGURÉ
→ prod live sur rebsam.fr
```

> **Cloud Run GitHub auto-deploy** : ✅ Configuré et actif. Chaque push sur `main` déclenche automatiquement un nouveau build/deploy via Cloud Build.

## Cloud Build — Trigger proxy (Cloud Run)
| Paramètre | Valeur |
|---|---|
| Projet GCP | `rebbe-sam-agent` |
| Service Cloud Run | `rebsam-proxy` |
| Région | `europe-west1` |
| Artifact Registry | `europe-west1-docker.pkg.dev` |
| Repository AR | `cloud-run-source-deploy` |
| Branche déclencheur | `main` |
| Config build | Inline YAML (Intégré — pas de cloudbuild.yaml dans le repo) |
| Compte de service | `217121855341-compute@developer.gserviceaccount.com` |
| Trigger ID | `f0a9130a-3562-435f-835c-a939c67c2f21` |

> Le YAML de build est intégré directement dans le trigger GCP (emplacement "Intégré"). Aucun fichier `cloudbuild.yaml` n'est requis dans le repo.

## Règles importantes
- Ne jamais committer de clés API ou secrets
- Le service worker est network-first pour index.html (pas de cache agressif)
- Les icônes PNG réelles sont dans icon-192.png et icon-512.png
- Le proxy tourne sur Cloud Run, séparé du frontend

## Design system — Chat UI

### Dégradé identitaire (à utiliser partout en remplacement de l'or)
```
linear-gradient(135deg, #5B8EF0 0%, #7C6FCD 50%, #E07B5A 100%)
```
Ce dégradé bleu→violet→corail est le fil conducteur visuel :
- Bouton CTA hero "Pose ta première question à RebSam"
- `<hr>` séparateurs dans les bulles Sam
- Titres h1/h2/h3 dans les bulles Sam
- Label "Séfarim consultés" (gradient text)
- Bordure gauche des source chips
- Avatar Sam

### Icônes
- Source chips : SVG Feather book (inline), PAS d'emoji
- Éviter les emoji décoratifs dans l'UI chrome (réservés au contenu IA)

### Typographie chat
- Corps bulles Sam : `font-family: 'Outfit', 'Inter', sans-serif`
- Titres (h1/h2/h3 markdown) : `Outfit` + gradient text

### Markdown dans les bulles
- `marked.js` (cdn.jsdelivr.net/npm/marked) — `gfm: true, breaks: true`
- Fallback JS si marked non chargé : gère `---` → `<hr>`, `**` → `<b>`, `*` → `<em>`, `#` → `<strong>`
- `---` du prompt → `<hr>` stylé avec le dégradé identitaire (hauteur 2px)

## PWA — manifest.json (état [2026-03-23])
| Champ | Valeur |
|---|---|
| `id` | `fr.rebsam.app` |
| `display_override` | `["window-controls-overlay", "standalone", "minimal-ui"]` |
| `related_applications` | Play Store `com.rebsam.app` |
| `iarc_rating_id` | placeholder à remplacer (Play Console → Classification du contenu) |
| `screenshots` | `screenshot-mobile.png` (1170×2526) + `screenshot-wide.png` (997×900) |
| Score PWABuilder | ~23/45 avant deploy — à re-tester après merge |

## Corpus Vertex AI Search — Répartition réelle (1972 docs)

| Niveau | Label | Nb docs | Contenu principal |
|---|---|---|---|
| 1 | Primaire (Talmud / Rambam / Tur) | 1286 | Talmud Bavli (361), Mishna (313), Nevi'im (182), Houmach (119), Ktouvim (96), Tur (96), Rambam (47) |
| 2 | Codificateur (ShA / MB / Responsa) | 29 | שאלות ותשובות / Responsa (23), ילקוט שמעוני (6) |
| 3 | Acharonim classiques | 141 | Sifrey Halacha (55), Parashat Shavua (39), חגי ומועדי ישראל (25), Halakha (22) |
| 4 | Thématique / Hassidout | 516 | Kabbalah (169), ספרי ברסלב (129), Moussar (54), הדרך לתורה (30), קונטרסים (29), Choutim 2 (21), etc. |

> **Note clé** : Niveau 2 n'a que 29 docs (Responsa uniquement). Les Sifrey Halacha (ShA, MB, Posqim) sont en **Niveau 3**. Le moteur halacha pratique est Niveau 3.

## Boost profiles — `proxy/main.py` (`_BOOST_PROFILES`)

| Profil | N1 | N2 | N3 | N4 | Usage |
|---|---|---|---|---|---|
| `halakha` | +0.2 | +0.7 | **+0.8** | -0.2 | Questions pratiques halacha |
| `rishonim` | +0.6 | +0.2 | **+0.9** | -0.1 | Rashi, Tosafot, Rambam, Ramban |
| `talmud` | **+0.9** | +0.1 | +0.3 | -0.2 | Guemara, Tanach, Midrash |
| `kabbalah` | +0.1 | -0.2 | 0.0 | **+0.9** | Zohar, Arizal, Hassidout, Breslav |
| `aggada` | +0.6 | 0.0 | +0.3 | **+0.5** | Moussar, Aggada, Hassidout |

> Prochaine étape pour affiner : ajouter un champ `source_category` dans les métadonnées Vertex AI pour booster par sous-catégorie (ex. Sifrey Halacha > Parashat Shavua dans un profil halacha).

## Hébergement frontend
| Paramètre | Valeur |
|---|---|
| Plateforme | Cloudflare Pages (remplace Netlify) |
| Projet CF | `rebsam-github-io` |
| URL CF | `rebsam-github-io.pages.dev` |
| Domaine custom | `rebsam.fr` |
| Auto-deploy | Push sur `main` → deploy instantané |
| Config | `_redirects` + `_headers` (racine du repo) |
| Netlify | Désactivé (conservé pour rollback) |

## Logging conversations — Make.com → Google Sheets
| Paramètre | Valeur |
|---|---|
| Scénario Make.com | "Chat Web Reb Sam" (ID 4651925, team 1121479) |
| Webhook Make.com | `https://hook.eu1.make.com/7p7pv9nkm8tqeyhc8sspve9u3nnarxt8` |
| Variable Cloud Run | `MAKE_LOG_WEBHOOK` |
| Google Sheet | "RebSam Testeurs" (yonatan26@gmail.com) |
| Colonnes | Date, Canal, Nom, Langue, Question, Réponse (500 chars), Session, Tours |
| Canaux loggés | `web` (chat rebsam.fr) + `whatsapp` |
| Fonction proxy | `log_to_make()` → fire & forget, non-bloquant |

## iOS App Store — Capacitor (état [2026-03-25])

### Setup effectué (branche `claude/setup-capacitor-ios-uZ5n6`)
| Fichier | Rôle |
|---|---|
| `capacitor.config.ts` | `appId: fr.rebsam.app`, `server.url: https://rebsam.fr`, `webDir: www` |
| `package.json` | Deps : `@capacitor/core`, `@capacitor/cli`, `@capacitor/ios`, `typescript` |
| `ios/App/App.xcodeproj/` | Projet Xcode — bundle ID `fr.rebsam.app`, iOS 13+ |
| `ios/App/App/Info.plist` | `WKAppBoundDomains: rebsam.fr`, portrait only, privacy strings |
| `ios/App/Podfile` | CocoaPods — pod install sur Mac |
| `www/index.html` | Placeholder webDir (contenu réel depuis rebsam.fr) |
| `codemagic.yaml` | Build cloud Mac mini M2 → TestFlight auto |

### Build sans Mac → Codemagic CI
- Compte Apple Developer 99$/an requis (pas encore souscrit)
- Flow : push `main` → Codemagic (mac_mini_m2) → pod install → xcodebuild → IPA → TestFlight
- À configurer dans Codemagic UI : signing Apple Developer + `APP_STORE_APPLE_ID`

### Icônes iOS
- 18 tailles générées depuis `icon-512.png` (upscalé)
- **À remplacer** : icône finale à décider (version A dégradé+RebSam ou B dégradé+RS)
- L'utilisateur fournira l'image source 2026-03-26

### Prochaines étapes iOS
1. Valider l'icône finale → régénérer toutes les tailles
2. Splash screen iOS (LaunchScreen.storyboard)
3. Screenshots App Store (FR/EN/HE)
4. Souscrire Apple Developer Program (99$/an)
5. Connecter Codemagic + lancer premier build
6. Metadata App Store Connect

- Public cible : US + Israël (majorité iPhone)

## État actuel / En cours
- Voir TASKS.md
- Migration Netlify → Cloudflare Pages ✅ terminée (2026-03-25)
- Make.com logging ✅ configuré (2026-03-25)

## Design system — Couleurs de fond
| Zone | Couleur | Note |
|---|---|---|
| `#chat-box` | `#f8fafc` | Blanc-gris neutre |
| `.chat-input-area` | `#f0f4fb` | Bleuté léger, harmonisé header |
| `.chat-header` | `linear-gradient(135deg, #5B8EF0 0%, #7C6FCD 50%, #E07B5A 100%)` | Dégradé identitaire standard |
