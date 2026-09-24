#!/usr/bin/env bash
# Fast path: build locally, upload the prebuilt static site.
#
# WARNING: this ships ONLY the contents of dist/. The serverless functions
# under api/ are not part of that bundle, so deploying this way removes them
# from production -- grading, certificates and the leaderboard all stop
# working until a full `npm run deploy` puts them back.
#
# Use it only for content-only changes when you are confident api/ has not
# changed, and prefer `npm run deploy` otherwise.
set -euo pipefail

if [ -d api ] && [ -z "${PCH_ALLOW_STATIC_DEPLOY:-}" ]; then
  echo "api/ exists, and this deploy path would drop it from production." >&2
  echo "Use: npm run deploy" >&2
  echo "Or, if you really mean it: PCH_ALLOW_STATIC_DEPLOY=1 npm run deploy:static" >&2
  exit 1
fi

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
