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

## État actuel / En cours
<!-- Mettre à jour cette section à chaque session avant de fermer -->
- Voir TASKS.md
