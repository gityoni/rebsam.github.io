# Audit du prompt RebSam

Effectue un audit complet du système de prompt de RebSam en testant le proxy live avec des questions de référence.

## Étape 1 — Lire le prompt actuel

Lire le fichier `index.js` et extraire le SYSTEM_PROMPT (lignes 9-80 environ). Identifier :
- Les règles TYPE 1 / TYPE 2 / TYPE 3
- Les RÈGLES UNIVERSELLES (ton, formatage, langue)
- Le DISCLAIMER

## Étape 2 — Lancer les tests

Proxy URL : `https://rebsam-proxy-217121855341.europe-west1.run.app`
Token : `rebsam-make-2026`

Envoyer chaque question ci-dessous via curl (une par une, attendre la réponse complète) :

```bash
curl -s -X POST "https://rebsam-proxy-217121855341.europe-west1.run.app" \
  -H "Content-Type: application/json" \
  -H "x-secret-token: rebsam-make-2026" \
  -d '{"prompt": "QUESTION_ICI", "history": []}' \
  --max-time 30
```

### Batterie de tests

**TYPE 1 — Halakhique pratique (doit utiliser 📜 LA HALAKHA + sources)**
- T1a : `Puis-je manger du fromage après de la viande de poulet ?`
- T1b : `Est-ce que je peux chauffer des aliments dans un four à micro-ondes non cachère ?`
- T1c : `Quelle bénédiction fait-on sur les pistaches ?`

**TYPE 2 — Personnel/émotionnel (doit commencer par l'écoute, PAS la Halakha)**
- T2a : `Je me sens très seul depuis que ma femme est partie, je ne sais plus quoi faire`
- T2b : `Mon fils adolescent refuse de prier et cela me brise le coeur`

**TYPE 3 — Intellectuel/kabbalistique/académique (réponse directe, SANS 📜 LA HALAKHA)**
- T3a : `Que dit le Arizal sur le petit Aleph de Vayikra ?`
- T3b : `Quelle est la différence entre les Tanaïm et les Amoraïm ?`
- T3c : `Que dit le Zohar sur la création du monde ?`
- T3d : `Pourquoi Rachi et le Rambam divergent-ils sur la nature des anges ?`

**CAS LIMITES — détection correcte**
- CL1 : `Ma mère non-juive m'a préparé un repas avec de la viande, dois-je le manger ?` (TYPE 1, aspect familial → Halakha d'abord)
- CL2 : `Comment les Amoraïm appliquaient-ils la Halakha de Chabbat ?` (TYPE 3, académique, PAS TYPE 1)

## Étape 3 — Évaluer chaque réponse

Pour chaque réponse, vérifier ces critères et noter ✅ ou ❌ :

| Critère | Description |
|---------|-------------|
| **TYPE_OK** | La structure correspond au bon type (T1=Halakha, T2=Écoute, T3=Direct) |
| **NO_FILLER** | Pas d'intro inutile ("B'ezrat Hashem, regardons...", "Voici la réponse...") |
| **DIRECT** | Répond clairement à la question posée |
| **SOURCES** | Cite des sources précises (Choulhan Aroukh, siman X, etc.) pour T1/T3 |
| **NO_T1_STRUCT** | Pas de "📜 LA HALAKHA" ni "CONCLUSION PRATIQUE" pour T2/T3 |
| **DISCLAIMER** | Contient le disclaimer IA à la fin |
| **LANGUE** | Répond en français |

## Étape 4 — Rapport d'audit

Générer un rapport structuré :

```
═══════════════════════════════════════════
  AUDIT PROMPT REBSAM — [date]
═══════════════════════════════════════════

SCORE GLOBAL : X/10

RÉSULTATS PAR TEST :
┌─────┬────────────┬───────────┬───────────┬──────────┬───────────┬──────────────┬──────────┐
│ ID  │ TYPE_OK    │ NO_FILLER │ DIRECT    │ SOURCES  │ NO_T1_STR │ DISCLAIMER   │ LANGUE   │
├─────┼────────────┼───────────┼───────────┼──────────┼───────────┼──────────────┼──────────┤
│ T1a │ ✅/❌      │ ✅/❌     │ ✅/❌     │ ✅/❌    │ ✅/❌     │ ✅/❌        │ ✅/❌    │
...
└─────┴────────────┴───────────┴───────────┴──────────┴───────────┴──────────────┴──────────┘

PROBLÈMES DÉTECTÉS :
- [liste des ❌ avec extrait de la réponse problématique]

RECOMMANDATIONS :
- [changements suggérés dans index.js]
═══════════════════════════════════════════
```

Afficher aussi les 2-3 premières lignes de chaque réponse pour permettre une validation visuelle rapide.

Si une question échoue plusieurs critères, proposer directement la correction à apporter dans le SYSTEM_PROMPT de `index.js`.
