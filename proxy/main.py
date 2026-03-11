"""
RebSam Cloud Run Proxy — v2 avec mémoire conversationnelle
Gère les appels Gemini multi-tour via l'historique de conversation.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
import google.auth
import google.auth.transport.requests
import requests as http_requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ── Config ───────────────────────────────────────────────
SECRET_TOKEN   = os.environ.get("SECRET_TOKEN", "rebsam-make-2026")
PROJECT_ID     = os.environ.get("GCP_PROJECT", "rebsam")
LOCATION       = os.environ.get("GCP_LOCATION", "europe-west1")
MODEL          = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")

VERTEX_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent"
)

SYSTEM_FALLBACK = (
    "Tu es RebSam, expert en Halacha (loi juive). "
    "Réponds avec les sources exactes (Choulhan Aroukh, Poskim). "
    "Sois précis, structuré et respectueux."
)

# ── Auth Google ───────────────────────────────────────────
def get_access_token():
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


# ── Construction du payload Gemini multi-tour ─────────────
def build_gemini_payload(system_prompt: str, history: list, message: str) -> dict:
    """
    Convertit l'historique [{role, content}, ...] en format Gemini contents.
    Le dernier message de l'historique EST le message courant (déjà ajouté côté front).
    """
    contents = []

    for turn in history:
        role = turn.get("role", "user")
        # Gemini n'accepte que "user" et "model"
        if role not in ("user", "model"):
            role = "user"
        contents.append({
            "role": role,
            "parts": [{"text": turn.get("content", "")}]
        })

    # Si l'historique est vide ou ne se termine pas par le message courant, l'ajouter
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

    # ── Lecture des paramètres (POST JSON ou GET query) ──
    if request.method == "POST" and request.is_json:
        data = request.get_json(force=True, silent=True) or {}
        system_prompt = data.get("systemPrompt", "")
        message       = data.get("message", "")
        history       = data.get("history", [])   # [{role, content}, ...]
        lang          = data.get("lang", "fr")
        # Rétrocompatibilité : si history vide mais prompt présent
        if not history and data.get("prompt"):
            message = data["prompt"]
            history = [{"role": "user", "content": message}]
    else:
        # Ancien format GET (rétrocompatibilité)
        prompt  = request.args.get("prompt", "")
        lang    = request.args.get("lang", "fr")
        message = prompt
        system_prompt = ""
        history = [{"role": "user", "content": prompt}]

    if not message and not history:
        return jsonify({"error": "No message provided"}), 400

    logging.info(f"[RebSam] lang={lang} history_turns={len(history)} msg={message[:80]}")

    # ── Appel Vertex AI Gemini ──
    payload = build_gemini_payload(system_prompt, history, message)

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

        # Extraction de la réponse
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
