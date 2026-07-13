#!/usr/bin/env bash
# Build locally, deploy prebuilt to Vercel (skips Vercel-side build).
set -euo pipefail

echo "==> Building locally..."
npm run build

echo "==> Wrapping dist/ in Build Output API..."
rm -rf .vercel/output
mkdir -p .vercel/output/static
printf '{"version":3}' > .vercel/output/config.json
cp -r dist/. .vercel/output/static/

echo "==> Deploying prebuilt to production..."
npx vercel deploy --prebuilt --prod

echo "==> Done."
