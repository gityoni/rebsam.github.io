"""
RebSam Cloud Run Proxy — v5 architecture directe (sans Make.com)
- Chat sync   : Site → Proxy → Gemini → réponse rapide
- WhatsApp    : Meta → /webhook → Gemini → WhatsApp Cloud API (direct, sans Make)
- Historique  : Firestore (collection wa_history, clé = numéro de téléphone)
- Log async   : Proxy → Make.com (fire & forget, non-bloquant, optionnel)
"""

import os
import re
import json
import logging
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify, make_response
import google.auth
import google.auth.transport.requests
import requests as http_requests
from google.cloud import firestore

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-secret-token",
}

@app.after_request
def add_cors(resp):
    for k, v in CORS_HEADERS.items():
        resp.headers[k] = v
    return resp

# ── Config ────────────────────────────────────────────────
SECRET_TOKEN       = os.environ.get("SECRET_TOKEN", "rebsam-make-2026")
PROJECT_ID         = os.environ.get("GCP_PROJECT", "rebbe-sam-agent")
LOCATION           = os.environ.get("GCP_LOCATION", "europe-west1")
MODEL              = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-001")
MAKE_LOG_WEBHOOK   = os.environ.get("MAKE_LOG_WEBHOOK", "")

# ── Config WhatsApp Cloud API (Meta) ──────────────────────
WHATSAPP_TOKEN     = os.environ.get("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID  = os.environ.get("WHATSAPP_PHONE_ID", "")
WEBHOOK_VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN", "rebsam-webhook-2026")

# ← Pour modifier le prompt sans rebuild : Cloud Console → Cloud Run → Variables d'env → SYSTEM_PROMPT
SYSTEM_PROMPT_ENV  = os.environ.get("SYSTEM_PROMPT", "")

VERTEX_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent"
)

# ── Firestore ─────────────────────────────────────────────
FIRESTORE_COLLECTION = "wa_history"
MAX_WA_HISTORY_TURNS = 10

try:
    db = firestore.Client()
    logging.info("[RebSam] Firestore initialisé")
except Exception as _e:
    db = None
    logging.warning(f"[RebSam] Firestore non disponible : {_e}")


def load_history(phone: str) -> list:
    if db is None:
        return []
    try:
        doc = db.collection(FIRESTORE_COLLECTION).document(phone).get()
        if doc.exists:
            return doc.to_dict().get("history", [])
    except Exception as e:
        logging.warning(f"[RebSam] Firestore load_history échoué : {e}")
    return []


def save_history(phone: str, history: list):
    if db is None:
        return
    try:
        db.collection(FIRESTORE_COLLECTION).document(phone).set({
            "history":    history,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logging.warning(f"[RebSam] Firestore save_history échoué : {e}")


# ── Prompt ────────────────────────────────────────────────
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
→ Si la situation manque de détails importants, POSE UNE OU DEUX QUESTIONS CIBLÉES avant de répondre.
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
📜 LA HALAKHA : Règle claire. Divergences Ashkénaze (Rama/Mishna Beroura) vs Séfarade (Maran/Yalkout Yossef).
✨ LE SENS PROFOND (LA LUMIÈRE) : Enseignement Sod ou moral (Likoutey Halachot, Ari zal, Ben Ich Haï, Zohar, Tanya).
📍 CONCLUSION PRATIQUE (LÉ-MAASSÉ) : 1-2 phrases concrètes.
📖 SOURCES PRÉCISES : "Nom du Livre, Siman X, Seif Y".

═══════════════════════════════════════════════
RÈGLES UNIVERSELLES
═══════════════════════════════════════════════
TON : Sage, humble et bienveillant. Utilise des termes hébraïques appropriés (Baroukh Hashem, Néchama, Hatslaha...) tout en restant compréhensible.
FORMATAGE : PAS de #/##/###. TITRES en MAJUSCULES avec emojis. Gras avec *astérisques*. Listes: 🔹 technique, 💡 conseils, 📖 sources. Deux lignes entre chaque section.
LANGUE : Réponds toujours dans la langue de l'utilisateur (FR/HE/EN).
CONTINUITÉ : Si l'utilisateur pose une question de suivi, tiens compte du contexte de la conversation précédente.
HUMILITÉ : Si une question dépasse le cadre halakhique ou nécessite un suivi professionnel, oriente avec douceur.

═══════════════════════════════════════════════
DISCLAIMER — DISCRET ET NON INTRUSIF
═══════════════════════════════════════════════
À la FIN de chaque réponse, ajoute toujours cette ligne discrète :

---
_🤖 RebSam est une IA — ses réponses ne remplacent pas le Psak d'un Rav. Pour toute décision halakhique engageante, consultez votre Rav._

- FR : _🤖 RebSam est une IA — ses réponses ne remplacent pas le Psak d'un Rav. Pour toute décision halakhique engageante, consultez votre Rav._
- EN : _🤖 RebSam is an AI — its answers do not replace a Rav's Psak. For any binding Halachic decision, please consult your Rav._
- HE : _🤖 רבסם הוא בינה מלאכותית — תשובותיו אינן מחליפות פסק רב. לכל החלטה הלכתית מחייבת, יש להתייעץ עם הרב שלכם._"""


def _load_prompt() -> str:
    try:
        with open("prompt.txt", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                logging.info("[RebSam] Prompt chargé depuis prompt.txt")
                return content
    except FileNotFoundError:
        pass
    if SYSTEM_PROMPT_ENV:
        logging.info("[RebSam] Prompt chargé depuis variable d'environnement")
        return SYSTEM_PROMPT_ENV
    logging.info("[RebSam] Prompt hardcodé utilisé")
    return SYSTEM_FALLBACK


ACTIVE_PROMPT = _load_prompt()


# ── Auth Google ────────────────────────────────────────────
def get_access_token():
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


# ── Log async vers Make.com (optionnel, fire & forget) ────
def _send_log(payload: dict):
    if not MAKE_LOG_WEBHOOK:
        return
    try:
        http_requests.post(MAKE_LOG_WEBHOOK, json=payload, timeout=10)
        logging.info("[RebSam] Log Make.com envoyé")
    except Exception as e:
        logging.warning(f"[RebSam] Log Make.com échoué (non-bloquant) : {e}")


def log_to_make(data: dict, reply: str):
    log_payload = {
        "sessionId": data.get("sessionId", ""),
        "name":      data.get("name", "Anonyme"),
        "lang":      data.get("lang", "fr"),
        "message":   data.get("message", ""),
        "reply":     reply,
        "timestamp": data.get("timestamp", ""),
        "turns":     len(data.get("history", [])),
        "channel":   data.get("channel", "web"),
    }
    threading.Thread(target=_send_log, args=(log_payload,), daemon=True).start()


# ── Détection de langue ───────────────────────────────────
_HEBREW_WORDS = re.compile(
    r'\b(chabbat|shabbat|kashrout|kosher|halakha|halacha|mitsva|mitsvot|mitzvot|torah|'
    r'havdala|kiddouch|tefilin|mezouza|tsitsit|shalom|chalom|pesach|roch hachana|'
    r'yom kippour|souccot|hanoucca|pourim|sefer|posek|psak|rav|rabbi|talmud|gemara|'
    r'mishna|zohar|tanya|ketouba|guet)\b',
    re.IGNORECASE
)
_FRENCH_WORDS = re.compile(
    r'\b(je|tu|il|nous|vous|ils|le|la|les|de|du|un|une|est|sont|avec|pour|dans|sur|que|qui)\b',
    re.IGNORECASE
)

def detect_language(text: str) -> str:
    hebrew_chars = len(re.findall(r'[\u05D0-\u05FF]', text))
    total_chars  = len(text.replace(' ', '')) or 1
    if hebrew_chars / total_chars > 0.2:
        return 'he'
    if (_HEBREW_WORDS.search(text) or
            re.search(r'[àâäéèêëîïôùûüç]', text, re.IGNORECASE) or
            _FRENCH_WORDS.search(text)):
        return 'fr'
    return 'en'


# ── Formatage WhatsApp ─────────────────────────────────────
def format_for_whatsapp(text: str) -> str:
    """Convertit markdown Gemini → format WhatsApp natif."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    text = re.sub(r'__(.+?)__', r'*\1*', text)
    text = re.sub(r'\n?---\n?', '\n\n', text)
    return text.strip()


# ── Construction payload Gemini multi-tour ────────────────
def build_gemini_payload(system_prompt: str, history: list, message: str) -> dict:
    contents = []
    for turn in history:
        role = turn.get("role", "user")
        if role not in ("user", "model"):
            role = "user"
        contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})
    if not contents or contents[-1].get("parts", [{}])[0].get("text") != message:
        contents.append({"role": "user", "parts": [{"text": message}]})
    return {
        "systemInstruction": {"parts": [{"text": system_prompt or SYSTEM_FALLBACK}]},
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
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
    }


# ── Envoi de la réponse via WhatsApp Cloud API ────────────
def send_whatsapp_reply(to: str, text: str):
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logging.warning("[RebSam/WA] WHATSAPP_TOKEN ou WHATSAPP_PHONE_ID manquant — réponse non envoyée")
        return
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
    resp = http_requests.post(
        url,
        headers={
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type":  "application/json",
        },
        json={
            "messaging_product": "whatsapp",
            "to":   to,
            "type": "text",
            "text": {"body": text},
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


# ── Traitement d'un message WhatsApp (en arrière-plan) ────
def process_wa_event(payload: dict):
    """
    Reçoit le payload brut de Meta, extrait le message,
    appelle Gemini et renvoie la réponse via WhatsApp Cloud API.
    Exécuté dans un thread séparé pour répondre 200 à Meta immédiatement.
    """
    try:
        entry  = (payload.get("entry") or [{}])[0]
        change = (entry.get("changes") or [{}])[0].get("value", {})

        messages = change.get("messages", [])
        if not messages:
            return  # status update (sent/delivered/read), ignorer

        msg = messages[0]
        if msg.get("type") != "text":
            logging.info(f"[RebSam/WA] Type non-texte ignoré : {msg.get('type')}")
            return

        phone   = msg.get("from", "")
        text    = msg.get("text", {}).get("body", "").strip()
        contacts = change.get("contacts") or [{}]
        name    = (contacts[0].get("profile") or {}).get("name", "Utilisateur")

        if not phone or not text:
            return

        logging.info(f"[RebSam/WA] Message de ****{phone[-4:]} ({name}) : {text[:80]}")

        # 1. Historique depuis Firestore
        history = load_history(phone)
        if len(history) > MAX_WA_HISTORY_TURNS:
            history = history[-MAX_WA_HISTORY_TURNS:]

        # 2. Détection langue
        lang = detect_language(text)

        # 3. Prompt : base + date + instructions WA
        today_str = datetime.now(timezone.utc).strftime("%A %d %B %Y")
        date_injection = {
            "he": f"\n\nהתאריך של היום (UTC): {today_str}.",
            "en": f"\n\nToday's date (UTC): {today_str}.",
        }.get(lang, f"\n\nDate d'aujourd'hui (UTC) : {today_str}.")

        wa_note = {
            "he": "\n\nאתה מגיב דרך WhatsApp. השתמש ב-*מודגש* (כוכבית אחת), _נטוי_, ואמוג'י. אל תשתמש בכותרות markdown (#).",
            "en": "\n\nYou are responding via WhatsApp. Use *bold* (single asterisk), _italic_, and emojis. Avoid markdown headers (#).",
        }.get(lang, "\n\nTu réponds via WhatsApp. Utilise *gras* (un seul astérisque), _italique_, et des emojis. Évite les titres markdown (#).")

        effective_system = ACTIVE_PROMPT + date_injection + wa_note
        gemini_payload   = build_gemini_payload(effective_system, history, text)

        # 4. Appel Gemini
        access_token = get_access_token()
        resp = http_requests.post(
            VERTEX_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type":  "application/json",
            },
            json=gemini_payload,
            timeout=60,
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
            logging.warning(f"[RebSam/WA] Réponse vide de Gemini : {gemini_data}")
            reply = {
                "fr": "Chalom ! Je n'ai pas pu générer de réponse. Veuillez réessayer. 🙏",
                "en": "Shalom! I could not generate a response. Please try again. 🙏",
                "he": "שלום! לא הצלחתי ליצור תשובה. אנא נסה שוב. 🙏",
            }.get(lang, "Chalom ! Je n'ai pas pu générer de réponse. 🙏")

        # 5. Nettoyage + formatage WhatsApp
        reply    = re.sub(r'^#{1,6}\s+', '', reply, flags=re.MULTILINE)
        reply_wa = format_for_whatsapp(reply)

        # 6. Envoi via WhatsApp Cloud API
        send_whatsapp_reply(phone, reply_wa)
        logging.info(f"[RebSam/WA] Réponse envoyée à ****{phone[-4:]}")

        # 7. Mise à jour historique Firestore
        updated = history + [
            {"role": "user",  "content": text},
            {"role": "model", "content": reply},
        ]
        if len(updated) > MAX_WA_HISTORY_TURNS:
            updated = updated[-MAX_WA_HISTORY_TURNS:]
        save_history(phone, updated)

        # 8. Log optionnel Make.com
        log_to_make({
            "sessionId": phone,
            "name":      name,
            "lang":      lang,
            "message":   text,
            "history":   history,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channel":   "whatsapp",
        }, reply)

    except Exception as e:
        logging.error(f"[RebSam/WA] Erreur traitement webhook : {e}", exc_info=True)


# ══════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════

# ── GET /webhook — vérification Meta ──────────────────────
@app.route("/webhook", methods=["GET"])
def webhook_verify():
    """
    Meta envoie une requête GET pour vérifier le webhook lors de l'inscription.
    https://developers.facebook.com/docs/graph-api/webhooks/getting-started
    """
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logging.info("[RebSam/WA] Webhook Meta vérifié avec succès")
        return challenge, 200

    logging.warning(f"[RebSam/WA] Vérification webhook échouée — token={token!r}")
    return "Forbidden", 403


# ── POST /webhook — réception des messages WhatsApp ───────
@app.route("/webhook", methods=["POST"])
def webhook_receive():
    """
    Reçoit les messages WhatsApp de Meta.
    Répond 200 immédiatement, traite en arrière-plan.
    """
    payload = request.get_json(force=True, silent=True) or {}
    threading.Thread(target=process_wa_event, args=(payload,), daemon=True).start()
    return "OK", 200


# ── POST / — chat web synchrone ───────────────────────────
@app.route("/", methods=["GET", "POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return make_response("", 204, CORS_HEADERS)

    token = request.headers.get("x-secret-token", "")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST" and request.is_json:
        data          = request.get_json(force=True, silent=True) or {}
        system_prompt = data.get("systemPrompt", "")
        message       = data.get("message", "")
        history       = data.get("history", [])
        lang          = data.get("lang", "fr")
        if not history and data.get("prompt"):
            message = data["prompt"]
            history = [{"role": "user", "content": message}]
    else:
        prompt        = request.args.get("prompt", "")
        lang          = request.args.get("lang", "fr")
        message       = prompt
        system_prompt = ""
        history       = [{"role": "user", "content": prompt}]
        data          = {"message": message, "lang": lang, "history": history}

    if not message and not history:
        return jsonify({"error": "No message provided"}), 400

    logging.info(f"[RebSam] lang={lang} turns={len(history)} msg={message[:80]}")

    today_str = datetime.now(timezone.utc).strftime("%A %d %B %Y")
    date_injection = {
        "he": f"\n\nהתאריך של היום (UTC): {today_str}. השתמש בתאריך זה לכל חישוב לוח שנה יהודי או זמני תפילה.",
        "en": f"\n\nToday's date (UTC): {today_str}. Use this date for any Jewish calendar or prayer time calculations.",
    }.get(lang, f"\n\nDate d'aujourd'hui (UTC) : {today_str}. Utilise cette date pour tout calcul de calendrier juif ou horaires de prière.")

    effective_system = ACTIVE_PROMPT + date_injection
    payload = build_gemini_payload(effective_system, history, message)

    try:
        access_token = get_access_token()
        resp = http_requests.post(
            VERTEX_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type":  "application/json",
            },
            json=payload,
            timeout=60,
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

        reply = re.sub(r'^#{1,6}\s+', '', reply, flags=re.MULTILINE)
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
