'use strict';

const { GoogleAuth } = require('google-auth-library');

const SECRET_TOKEN = process.env.SECRET_TOKEN;
const PROJECT_ID   = process.env.PROJECT_ID   || 'rebbe-sam-agent';
const ENGINE_ID    = process.env.ENGINE_ID    || 'rebsam-brain_1772716977408';

const SYSTEM_PROMPT = `PROMPT SYSTÈME : REBSAM - EXPERT EN HALAKHA ET MASHPIA
═══════════════════════════════════════════════
PERSONA
═══════════════════════════════════════════════
Tu es Reb Sam, un Mashpia (guide spirituel) et expert en Halakha. Tu allies la profondeur de la Torah, la chaleur d'un Rav à l'écoute, et la précision d'un Posek.
Tu parles comme un Rav bienveillant qui VOIT la personne derrière la question.
STRICTEMENT INTERDIT : "mon enfant", "mon cher ami", "mon fils". Jamais de ton condescendant.
═══════════════════════════════════════════════
DÉTECTION DU TYPE DE QUESTION — CRUCIAL
═══════════════════════════════════════════════
TYPE 1 — QUESTION HALAKHIQUE TECHNIQUE (kashrout, Chabbat, bénédictions, produit, objet, règle précise) :
→ Applique directement la STRUCTURE HALAKHIQUE COMPLÈTE ci-dessous.
TYPE 2 — QUESTION PERSONNELLE / ÉMOTIONNELLE / RELATIONNELLE (couple, famille, souffrance, solitude, crise, doute spirituel, relations intimes, santé mentale, conflit) :
→ NE COMMENCE PAS par la Halakha. D'abord : ÉCOUTE et COMPRENDS.
→ Commence par valider l'émotion avec chaleur et empathie sincère.
→ Si la situation manque de détails importants, POSE UNE OU DEUX QUESTIONS CIBLÉES avant de répondre. Exemples : "Depuis combien de temps vivez-vous cette situation ?", "Y a-t-il des enfants impliqués ?", "Avez-vous déjà consulté un Rav ou un thérapeute à ce sujet ?"
→ Seulement APRÈS avoir écouté et compris : amène doucement l'éclairage de la Torah et de la Halakha.
→ Propose des pistes concrètes, des ressources (thérapeute de couple, Rav, etc.) si pertinent.
→ Structure pour ce type :
   🤝 ACCUEIL : Valide l'émotion. Montre que tu as VRAIMENT entendu.
   ❓ QUESTIONS (si nécessaire) : 1-2 questions pour mieux comprendre.
   💛 ÉCLAIRAGE DE LA TORAH : Sagesse applicable à cette situation humaine.
   📍 PISTES CONCRÈTES : Actions douces et réalistes.
   📖 SOURCES (optionnel, seulement si très pertinent).
═══════════════════════════════════════════════
STRUCTURE HALAKHIQUE COMPLÈTE (TYPE 1 uniquement)
═══════════════════════════════════════════════
INTRODUCTION : Chalom Aleichem, voici la réponse à votre question. (+ Hatslaha ou Néchama selon le contexte)
📜 LA HALAKHA : Règle claire. Divergences Ashkénaze (Rama/Mishna Beroura/נטעי גבריאל/פניני-הלכה) vs Séfarade (Maran/Yalkout Yossef/benishchai).
✨ LE SENS PROFOND (LA LUMIÈRE) : Enseignement Sod ou moral (Likoutey Halachot, Ari zal, Ben Ich Haï, Zohar, Tanya).
📍 CONCLUSION PRATIQUE (LÉ-MAASSÉ) : 1-2 phrases concrètes.
📖 SOURCES PRÉCISES : "Nom du Livre, Siman X, Seif Y".
═══════════════════════════════════════════════
RÈGLES UNIVERSELLES
═══════════════════════════════════════════════
TON : Sage, humble et bienveillant. Utilise des termes hébraïques appropriés (Baroukh Hashem, Shaliach, Néchama, Hatslaha, Simha, Emet...) tout en restant compréhensible. Ton style reflète la dignité d'un érudit en Torah.
FORMATAGE : PAS de #/##/###. TITRES en MAJUSCULES avec emojis. Gras avec *astérisques*. Listes: 🔹 technique, 💡 conseils, 📖 sources. Deux lignes entre chaque section.
LANGUE : Réponds toujours dans la langue de l'utilisateur (FR/HE/EN).
CONTINUITÉ : Si l'utilisateur pose une question de suivi, tiens compte du contexte de la conversation précédente.
HUMILITÉ : Si une question dépasse le cadre halakhique ou nécessite un suivi professionnel (médecin, thérapeute, Rav local), oriente avec douceur.
═══════════════════════════════════════════════
DISCLAIMER — DISCRET ET NON INTRUSIF
═══════════════════════════════════════════════
À la FIN de chaque réponse, ajoute toujours cette ligne discrète, séparée par une ligne vide :
---
_🤖 RebSam est une IA — ses réponses ne remplacent pas le Psak d'un Rav. Pour toute décision halakhique engageante, consultez votre Rav._
Cette ligne doit être courte, sobre, jamais répétée deux fois dans la même réponse, et adaptée à la langue de l'utilisateur :
- FR : _🤖 RebSam est une IA — ses réponses ne remplacent pas le Psak d'un Rav. Pour toute décision halakhique engageante, consultez votre Rav._
- EN : _🤖 RebSam is an AI — its answers do not replace a Rav's Psak. For any binding Halachic decision, please consult your Rav._
- HE : _🤖 רבסם הוא בינה מלאכותית — תשובותיו אינן מחליפות פסק רב. לכל החלטה הלכתית מחייבת, יש להתייעץ עם הרב שלכם._`;

async function getAccessToken() {
  const auth = new GoogleAuth({ scopes: ['https://www.googleapis.com/auth/cloud-platform'] });
  const client = await auth.getClient();
  const tokenResponse = await client.getAccessToken();
  return tokenResponse.token;
}

// FIX: query.text = question seule | preamble = SYSTEM_PROMPT + langue + historique
// FIX: queryId retiré | retry ajouté
async function searchAndAnswer(prompt, preamble, token) {
  const url = 'https://discoveryengine.googleapis.com/v1/projects/' + PROJECT_ID + '/locations/global/collections/default_collection/engines/' + ENGINE_ID + '/servingConfigs/default_search:answer';

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({
          query: { text: prompt },
          answerGenerationSpec: {
            modelSpec: { modelVersion: 'gemini-2.0-flash-001/answer_gen/v1' },
            promptSpec: { preamble: preamble },
            includeCitations: true
          }
        })
      });
      if (!response.ok) throw new Error('Discovery Engine HTTP ' + response.status);
      return response.json();
    } catch (err) {
      if (attempt === 0) await new Promise(r => setTimeout(r, 1000));
      else throw err;
    }
  }
}

// FIX: preamble passé en paramètre (inclut SYSTEM_PROMPT + langue + historique)
async function fallbackGemini(prompt, preamble, searchSnippets, token) {
  const url = 'https://aiplatform.googleapis.com/v1/projects/' + PROJECT_ID + '/locations/global/publishers/google/models/gemini-2.0-flash-001:generateContent';
  const snippetContext = searchSnippets.length > 0
    ? '\n\nEXTRAITS DES SOURCES (utilise-les pour ta réponse) :\n' + searchSnippets.join('\n---\n')
    : '';

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify({
      contents: [{ role: 'user', parts: [{ text: preamble + snippetContext + '\n\n' + prompt }] }]
    })
  });
  const data = await response.json();
  return data?.candidates?.[0]?.content?.parts?.[0]?.text || null;
}

// FIX: détection des mots hébreux translittérés (chabbat, kashrout, etc.)
const HEBREW_TRANSLITERATED = /\b(chabbat|shabbat|kashrout|kosher|halakha|halacha|mitsva|mitsvot|mitzvot|torah|havdala|kiddouch|tefilin|mezouza|tsitsit|shalom|chalom|pesach|roch hachana|yom kippour|souccot|hanoucca|pourim|sefer|posek|psak|rav|rabbi|talmud|gemara|mishna|zohar|tanya|ketouba|guet|choul|arba|loulav|etrog)\b/i;

function detectLanguage(text) {
  const hebrewChars = (text.match(/[\u05D0-\u05FF]/g) || []).length;
  const totalChars = text.replace(/\s/g, '').length || 1;
  if (hebrewChars / totalChars > 0.2) return 'he';
  if (HEBREW_TRANSLITERATED.test(text) ||
      (text.match(/[àâäéèêëîïôùûüç]/gi) || []).length > 0 ||
      /(je|tu|il|nous|vous|ils|le|la|les|de|du|un|une|est|sont|avec|pour|dans|sur|que|qui)\b/i.test(text)) return 'fr';
  return 'en';
}

exports.rebsamProxy = async (req, res) => {
  const allowedOrigin = process.env.ALLOWED_ORIGIN || 'https://rebsam.netlify.app';
  res.set('Access-Control-Allow-Origin', allowedOrigin);
  res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, x-secret-token');

  if (req.method === 'OPTIONS') { res.status(204).send(''); return; }

  if (!SECRET_TOKEN) return res.status(500).json({ error: 'Server misconfigured: missing SECRET_TOKEN env var' });
  const token = req.headers['x-secret-token'] || req.query.token;
  if (token !== SECRET_TOKEN) return res.status(401).json({ error: 'Unauthorized' });

  const prompt  = req.query.prompt || (req.body && req.body.prompt);
  const history = (req.body && req.body.history) || [];
  if (!prompt) return res.status(400).json({ error: 'Missing prompt' });

  try {
    const accessToken = await getAccessToken();

    // Détection langue + instructions
    const detectedLang = detectLanguage(prompt);
    const langInstructions = {
      fr: '\n\nIMPORTANT: Réponds UNIQUEMENT en français, quelle que soit la langue des sources.',
      he: '\n\nחשוב מאוד: ענה תמיד בעברית בלבד, ללא קשר לשפת המקורות.',
      en: '\n\nIMPORTANT: Always respond in English only, regardless of the language of the sources.'
    };

    // Construire le preamble complet : SYSTEM_PROMPT + langue + historique
    let preamble = SYSTEM_PROMPT + langInstructions[detectedLang];
    const recentHistory = history.slice(-12);
    if (recentHistory.length > 1) {
      preamble += '\n\nConversation précédente (pour assurer la continuité) :\n';
      for (const msg of recentHistory.slice(0, -1)) {
        const role = msg.role === 'user' ? 'Utilisateur' : 'RebSam';
        preamble += role + ': ' + msg.content.substring(0, 400) + '\n';
      }
    }

    const data = await searchAndAnswer(prompt, preamble, accessToken);
    const answerText = data?.answer?.answerText || '';

    const isFailure = !answerText ||
      answerText.includes('Impossible de générer') ||
      answerText.includes('Unable to generate') ||
      answerText.length < 10;

    if (!isFailure) return res.status(200).send(answerText);

    // Fallback Gemini : extraire les snippets des références Discovery Engine
    const snippets = (data?.answer?.references || [])
      .slice(0, 5)
      .filter(r => r?.chunkInfo?.content)
      .map(r => r.chunkInfo.content.substring(0, 600));

    const fallbackAnswer = await fallbackGemini(prompt, preamble, snippets, accessToken);
    if (fallbackAnswer) return res.status(200).send(fallbackAnswer);

    const fallbackMsg = {
      fr: 'Chalom Aleichem ! Je n\'ai pas trouvé de réponse précise dans le corpus. Pourriez-vous reformuler votre question ? 🙏',
      en: 'Shalom! I could not find a precise answer. Could you rephrase your question? 🙏',
      he: 'שלום עליכם! לא מצאתי תשובה מדויקת לשאלה זו. האם תוכלו לנסח מחדש? 🙏'
    };
    res.status(200).send(fallbackMsg[detectedLang]);

  } catch (err) {
    console.error('[rebsamProxy]', err);
    res.status(500).json({ error: err.message });
  }
};
