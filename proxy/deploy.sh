#!/bin/bash
# ─────────────────────────────────────────────
#  RebSam — Deploy script
#  Usage : cd ~/proxy && ./deploy.sh
# ─────────────────────────────────────────────
set -e

PROJECT="rebbe-sam-agent"
IMAGE="gcr.io/$PROJECT/rebsam-proxy"
SERVICE="rebsam-proxy"
REGION="europe-west1"

echo "🔨 Build de l'image..."
gcloud builds submit --tag "$IMAGE" --project "$PROJECT"

echo "🚀 Déploiement sur Cloud Run..."
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --project "$PROJECT"

echo "✅ Déployé ! URL : https://rebsam-proxy-217121855341.europe-west1.run.app"
