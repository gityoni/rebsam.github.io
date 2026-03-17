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
→ Cloud Run auto-deploy déclenché sur branche main (proxy) [À CONFIGURER]
→ prod live sur rebsam.fr
```

> **Cloud Run GitHub auto-deploy** : pas encore configuré. À faire : Cloud Run → Edit & Deploy New Revision → Continuously deploy from a repository → repo `gityoni/rebsam.github.io` → branch `^main$` → Dockerfile `/proxy/Dockerfile`.

## Règles importantes
- Ne jamais committer de clés API ou secrets
- Le service worker est network-first pour index.html (pas de cache agressif)
- Les icônes PNG réelles sont dans icon-192.png et icon-512.png
- Le proxy tourne sur Cloud Run, séparé du frontend

## État actuel / En cours
<!-- Mettre à jour cette section à chaque session avant de fermer -->
- Voir TASKS.md
