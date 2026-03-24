# Audit du prompt RebSam

Effectue un audit complet du système de prompt de RebSam en testant le proxy live avec des questions de référence.

## Étape 1 — Lire le prompt actuel

Lire le fichier `proxy/prompt.txt`. Identifier :
- Les règles TYPE 0 / TYPE 1 / TYPE 2 / TYPE 3 / TYPE 4
- L'architecture RAG (GROUNDED ONLY)
- Le PROFIL UTILISATEUR (nusach, niveau)
- La DÉTECTION CONTEXTUELLE (urgence, micro-empathie)
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

**TYPE 1 — Halakhique pratique (doit utiliser 📜 LA HALAKHA + sources RAG)**
- T1a : `Puis-je manger du fromage après de la viande de poulet ?`
- T1b : `Est-ce que je peux chauffer des aliments dans un four à micro-ondes non cachère ?`
- T1c : `Quelle bénédiction fait-on sur les pistaches ?`

**TYPE 2 — Personnel/émotionnel (doit commencer par 🤝 ACCUEIL, PAS la Halakha)**
- T2a : `Je me sens très seul depuis que ma femme est partie, je ne sais plus quoi faire`
- T2b : `Mon fils adolescent refuse de prier et cela me brise le coeur`

**TYPE 4 — Intellectuel/kabbalistique/académique en PREMIER MESSAGE (prose directe, SANS 📜 LA HALAKHA)**
- T4a : `Que dit le Arizal sur le petit Aleph de Vayikra ?`
- T4b : `Quelle est la différence entre les Tanaïm et les Amoraïm ?`
- T4c : `Que dit le Zohar sur la création du monde ?`
- T4d : `Pourquoi Rachi et le Rambam divergent-ils sur la nature des anges ?`

**CAS LIMITES — détection correcte**
- CL1 : `Ma mère non-juive m'a préparé un repas avec de la viande, dois-je le manger ?` (TYPE 1 + MICRO-EMPATHIE — une phrase chaleureuse AVANT la Halakha)
- CL2 : `Comment les Amoraïm appliquaient-ils la Halakha de Chabbat ?` (TYPE 4 académique, PAS TYPE 1)

## Étape 3 — Évaluer chaque réponse

Pour chaque réponse, vérifier ces critères et noter ✅ ou ❌ :

| Critère | Description |
|---------|-------------|
| **TYPE_OK** | Structure correcte (T1=Halakha, T2=Écoute, T4=Prose directe) |
| **NO_FILLER** | Pas d'intro inutile ("B'ezrat Hashem, regardons...", "Voici la réponse...") |
| **DIRECT** | Répond clairement à la question posée |
| **SOURCES_RAG** | Sources citées = issues du corpus RAG uniquement, jamais inventées. Si aucune source RAG → section 📖 ABSENTE (pas de "None", "N/A") |
| **NO_T1_STRUCT** | Pas de "📜 LA HALAKHA" ni "CONCLUSION PRATIQUE" pour T2/T4 |
| **DISCLAIMER** | Contient le disclaimer IA à la fin (sauf TYPE 0) |
| **LANGUE** | Répond en français |

## Étape 4 — Rapport d'audit

Générer un rapport structuré :

```
═══════════════════════════════════════════════════════
  AUDIT PROMPT REBSAM — [date]
  Modèle : claude-sonnet-4-6 via Vertex AI (us-east5)
  RAG : Vertex AI Search découplé (corpus-sifrey-global)
═══════════════════════════════════════════════════════

SCORE GLOBAL : X/11

RÉSULTATS PAR TEST :
┌──────┬──────────┬───────────┬────────┬─────────────┬───────────┬──────────────┬────────┐
│ ID   │ TYPE_OK  │ NO_FILLER │ DIRECT │ SOURCES_RAG │ NO_T1_STR │ DISCLAIMER   │ LANGUE │
├──────┼──────────┼───────────┼────────┼─────────────┼───────────┼──────────────┼────────┤
│ T1a  │ ✅/❌    │ ✅/❌     │ ✅/❌  │ ✅/❌       │ ✅/❌     │ ✅/❌        │ ✅/❌  │
│ T1b  │ ...
│ T1c  │ ...
│ T2a  │ ...
│ T2b  │ ...
│ T4a  │ ...
│ T4b  │ ...
│ T4c  │ ...
│ T4d  │ ...
│ CL1  │ ...
│ CL2  │ ...
└──────┴──────────┴───────────┴────────┴─────────────┴───────────┴──────────────┴────────┘

PROBLÈMES DÉTECTÉS :
- [liste des ❌ avec extrait de la réponse problématique]

RECOMMANDATIONS :
- [changements suggérés dans proxy/prompt.txt]
═══════════════════════════════════════════════════════
```

Afficher aussi les 2-3 premières lignes de chaque réponse pour permettre une validation visuelle rapide.

Si une question échoue plusieurs critères, proposer directement la correction à apporter dans `proxy/prompt.txt`.
