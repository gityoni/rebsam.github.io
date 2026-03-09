# CLAUDE.md — Mémoire du projet RebSam

## Description du projet

Site vitrine statique **RebSam** — assistant Torah & Halakha propulsé par IA.
Site unipage (SPA-like) déployé sur **Netlify**, hébergé sur GitHub Pages / GitHub repo `rebsam.github.io`.

---

## Stack technique

| Élément | Détail |
|---|---|
| Frontend | HTML/CSS/JS vanilla (pas de framework) |
| Hébergement | Netlify (CI/CD depuis GitHub) |
| Branche de dev | `claude/ai-website-google-cloud-V2c1R` |
| Automatisation | Make.com (webhooks) |
| PWA | `manifest.json` + `sw.js` (Service Worker) |

---

## Fichiers principaux

- `index.html` — page unique, tout le site (HTML + CSS + JS inline)
- `netlify.toml` — config Netlify (redirects, headers CSP, cache, Lighthouse plugin)
- `manifest.json` — config PWA
- `sw.js` — Service Worker (cache offline)

---

## Configurations clés

### Webhook Make.com
```js
const MAKE_WEBHOOK_URL = 'https://hook.eu1.make.com/r1woeelogkk0bv2i6s5cxu3mli231nbg';
```
- Utilisé par le chat flottant pour envoyer les messages utilisateur
- Autorisé dans la CSP : `connect-src 'self' https://hook.eu1.make.com`

### WhatsApp
- Numéro Meta test bot : `+1 (555) 179-0835`
- Lien : `https://wa.me/15551790835`
- Bouton flottant `#btn-wa` dans le HTML

### Langues supportées
- `FR` (français) — langue par défaut
- `עברית` (hébreu) — RTL, police Heebo
- `EN` (anglais)

### Mode sombre
- Basculement via `toggleDark()` + classe `html.dark`
- Icônes : ☀️ / 🌙 selon le mode

---

## Sécurité (netlify.toml)

Headers de sécurité actifs :
- `X-Frame-Options: DENY`
- `Content-Security-Policy` avec whitelist stricte
- `Strict-Transport-Security` (HSTS)
- `Permissions-Policy` (désactive caméra, micro, géoloc)

---

## Redirects Netlify

| URL | Destination | Code |
|---|---|---|
| `/halakha` | `/#faq` | 301 |
| `/ask` | `/#hero` | 301 |
| `/torah` | `/#sources` | 301 |
| `/*` | `/index.html` | 200 (fallback SPA) |

---

## Historique des décisions importantes

- **Chat web** → connecté au vrai webhook Make.com (plus de mock)
- **Bouton WhatsApp** → numéro Meta test bot pour sandbox WhatsApp Business
- **CSP** → `hook.eu1.make.com` autorisé explicitement
- **Hero section** → refonte UI, suppression bandeau stats noir
- **Dark mode** → icônes soleil/lune corrigées
- **AOS** → librairie d'animations au scroll intégrée
- **Netlify plugin Lighthouse** → audit perf automatique à chaque déploiement

---

## Branche Git

Toujours développer sur : `claude/ai-website-google-cloud-V2c1R`

```bash
git push -u origin claude/ai-website-google-cloud-V2c1R
```
