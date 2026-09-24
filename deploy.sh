#!/usr/bin/env bash
# Deploy the site AND the serverless API to Vercel.
#
# Vercel builds this one remotely. That is slower than the local prebuilt path
# (see deploy-static.sh) but it is the only way the functions under api/ get
# deployed: a --prebuilt upload ships exactly the files in .vercel/output, and
# the static-only bundle that script assembles contains none of them.
#
# Use this whenever anything under api/ has changed -- and by default, because
# deploying the static path afterwards would silently remove the API.
set -euo pipefail

echo "==> Checking the API can at least be parsed..."
for f in api/*.js api/_lib/*.js; do
  node --check "$f"
done

echo "==> Deploying to production (Vercel builds)..."
npx vercel deploy --prod

echo "==> Done."
echo
echo "Required environment variables on the Vercel project:"
echo "  FIREBASE_SERVICE_ACCOUNT  the service account JSON, on one line"
echo "  CRON_SECRET               any long random string; guards /api/send-digest"
