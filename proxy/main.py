"""
RebSam Cloud Run Proxy — v3 architecture pro
- Chat sync : Site → Proxy → Gemini → réponse rapide
- Log async : Proxy → Make.com (fire & forget, non-bloquant)
"""

import os
import json
import logging
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.auth
import google.auth.transport.requests
import requests as http_requests

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# ── Config ───────────────────────────────────────────────
SECRET_TOKEN      = os.environ.get("SECRET_TOKEN", "rebsam-make-2026")
PROJECT_ID        = os.environ.get("GCP_PROJECT", "rebbe-sam-agent")
LOCATION          = os.environ.get("GCP_LOCATION", "europe-west1")
MODEL             = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-001")
MAKE_LOG_WEBHOOK  = os.environ.get("MAKE_LOG_WEBHOOK", "https://hook.eu1.make.com/r1woeelogkk0bv2i6s5cxu3mli231nbg")

VERTEX_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent"
)

SYSTEM_FALLBACK = """═══════════════════════════════════════════════
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
📜 LA HALAKHA : Règle claire. Divergences Ashkénaze (Rama/Mishna Beroura/פנינה ההלכה) vs Séfarade (Maran/Yalkout Yossef/benishchai).
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
- HE : _🤖 רבסם הוא בינה מלאכותית — תשובותיו אינן מחליפות פסק רב. לכל החלטה הלכתית מחייבת, יש להתייעץ עם הרב שלכם._"""

# ── Auth Google ───────────────────────────────────────────
def get_access_token():
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


# ── Log async vers Make.com (fire & forget) ───────────────
def _send_log(payload: dict):
    """Envoie un log à Make.com en arrière-plan. N'impacte pas la réponse utilisateur."""
    if not MAKE_LOG_WEBHOOK:
        return
    try:
        http_requests.post(
            MAKE_LOG_WEBHOOK,
            json=payload,
            timeout=10
        )
        logging.info("[RebSam] Log Make.com envoyé")
    except Exception as e:
        logging.warning(f"[RebSam] Log Make.com échoué (non-bloquant) : {e}")


def log_to_make(data: dict, reply: str):
    """Lance le log Make.com dans un thread séparé pour ne pas bloquer la réponse."""
    log_payload = {
        "sessionId":  data.get("sessionId", ""),
        "name":       data.get("name", "Anonyme"),
        "lang":       data.get("lang", "fr"),
        "message":    data.get("message", ""),
        "reply":      reply,
        "timestamp":  data.get("timestamp", ""),
        "turns":      len(data.get("history", [])),
    }
    t = threading.Thread(target=_send_log, args=(log_payload,), daemon=True)
    t.start()


# ── Construction du payload Gemini multi-tour ─────────────
def build_gemini_payload(system_prompt: str, history: list, message: str) -> dict:
    contents = []

    for turn in history:
        role = turn.get("role", "user")
        if role not in ("user", "model"):
            role = "user"
        contents.append({
            "role": role,
            "parts": [{"text": turn.get("content", "")}]
        })

    if not contents or contents[-1].get("parts", [{}])[0].get("text") != message:
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })

    return {
        "systemInstruction": {
            "parts": [{"text": system_prompt or SYSTEM_FALLBACK}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "topP": 0.9
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
        ]
    }


# ── Route principale ──────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def chat():
    # Auth
    token = request.headers.get("x-secret-token", "")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    # ── Lecture des paramètres ──
    if request.method == "POST" and request.is_json:
        data = request.get_json(force=True, silent=True) or {}
        system_prompt = data.get("systemPrompt", "")
        message       = data.get("message", "")
        history       = data.get("history", [])
        lang          = data.get("lang", "fr")
        if not history and data.get("prompt"):
            message = data["prompt"]
            history = [{"role": "user", "content": message}]
    else:
        prompt  = request.args.get("prompt", "")
        lang    = request.args.get("lang", "fr")
        message = prompt
        system_prompt = ""
        history = [{"role": "user", "content": prompt}]
        data = {"message": message, "lang": lang, "history": history}

    if not message and not history:
        return jsonify({"error": "No message provided"}), 400

    logging.info(f"[RebSam] lang={lang} turns={len(history)} msg={message[:80]}")

    # Injecte la date réelle dans le prompt système
    today_str = datetime.now(timezone.utc).strftime("%A %d %B %Y")
    date_injection = f"\n\nDate d'aujourd'hui (UTC) : {today_str}. Utilise cette date pour tout calcul de calendrier juif ou horaires de prière."
    effective_system = (system_prompt or SYSTEM_FALLBACK) + date_injection

    # ── Appel Vertex AI Gemini (synchrone) ──
    payload = build_gemini_payload(effective_system, history, message)

    try:
        access_token = get_access_token()
        resp = http_requests.post(
            VERTEX_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        gemini_data = resp.json()

        reply = (
            gemini_data
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not reply:
            logging.warning(f"[RebSam] Réponse vide de Gemini : {gemini_data}")
            reply = "Je n'ai pas pu générer de réponse. Veuillez réessayer."

        # ── Log async vers Make.com (non-bloquant) ──
        log_to_make(data, reply)

        return jsonify({"reply": reply})

    except http_requests.HTTPError as e:
        logging.error(f"[RebSam] Vertex AI HTTP error: {e} — {resp.text[:500]}")
        return jsonify({"error": "Vertex AI error", "detail": str(e)}), 502
    except Exception as e:
        logging.error(f"[RebSam] Unexpected error: {e}")
        return jsonify({"error": "Internal error", "detail": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
