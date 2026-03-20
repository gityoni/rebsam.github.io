#!/bin/bash
# ─────────────────────────────────────────────
#  RebSam — Deploy script
#  Usage : cd proxy && ./deploy.sh
#
#  Variables d'environnement requises sur Cloud Run :
#    SECRET_TOKEN          — token auth chat web
#    WHATSAPP_TOKEN        — Bearer token WhatsApp Cloud API (Meta)
#    WHATSAPP_PHONE_ID     — Phone Number ID (Meta Business Manager)
#    WEBHOOK_VERIFY_TOKEN  — token de vérification webhook Meta
#    GEMINI_MODEL          — modèle LLM (défaut: claude-sonnet-4-6)
#                            claude-* → Claude via Vertex AI Model Garden (us-east5) + RAG découplé
#                            gemini-* → Gemini via Vertex AI (europe-west1) + RAG natif intégré
#    GCP_PROJECT           — projet GCP (défaut: rebbe-sam-agent)
#    GCP_LOCATION          — région Vertex AI Gemini (défaut: europe-west1)
#    MAKE_LOG_WEBHOOK      — (optionnel) webhook Make.com pour logs
# ─────────────────────────────────────────────
set -e

PROJECT="rebbe-sam-agent"
IMAGE="gcr.io/$PROJECT/rebsam-proxy"
SERVICE="rebsam-proxy"
REGION="europe-west1"

echo "Build de l'image..."
gcloud builds submit --tag "$IMAGE" --project "$PROJECT"

echo "Déploiement sur Cloud Run..."
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --project "$PROJECT"

echo "Déployé ! URL : https://rebsam-proxy-217121855341.europe-west1.run.app"
echo ""
echo "--- RAPPEL : variables à configurer dans Cloud Run ---"
echo "GEMINI_MODEL          = claude-sonnet-4-6  (ou gemini-* pour basculer)"
echo "WHATSAPP_TOKEN        = (token Meta permanent)"
echo "WHATSAPP_PHONE_ID     = (Phone Number ID Meta)"
echo "WEBHOOK_VERIFY_TOKEN  = rebsam-webhook-2026"
echo ""
echo "--- RAPPEL : configurer le webhook Meta ---"
echo "URL     : https://rebsam-proxy-217121855341.europe-west1.run.app/webhook"
echo "Token   : rebsam-webhook-2026"
echo "Champs  : messages"
