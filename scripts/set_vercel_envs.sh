#!/usr/bin/env bash
# set_vercel_envs.sh - Add environment variables to Vercel project from .env file
# Usage: VERCEL_TOKEN=your_token ./scripts/set_vercel_envs.sh <projectId> [--preview]

set -euo pipefail
PROJECT_ID="$1"
PREVIEW=false
if [ "${2:-}" = "--preview" ]; then PREVIEW=true; fi

if [ ! -f .env ]; then
  echo ".env file not found in repo root. Copy '.env.example' to '.env' and fill in values."
  exit 1
fi

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "VERCEL_TOKEN is not set; set it in the environment before running."
  exit 1
fi

while IFS= read -r line; do
  # skip blanks and comments
  [[ -z "$line" ]] && continue
  [[ "${line:0:1}" = "#" ]] && continue
  if [[ ! "$line" =~ .*=.* ]]; then continue; fi
  key="$([[ "$line" = *=* ]] && echo "${line%%=*}" | xargs)"
  value="$([[ "$line" = *=* ]] && echo "${line#*=}" | sed -e 's/^"//' -e 's/"$//' | xargs)"
  [[ "$key" = "VERCEL_TOKEN" ]] && continue
  [[ -z "$value" ]] && echo "Skipping $key (empty)" && continue

  environment=production
  if [ "$PREVIEW" = true ]; then environment=preview; fi

  echo "Setting $key=$environment"
  # Remove if exists (best effort) then add
  set +e
  vercel env rm "$key" "$PROJECT_ID" "$environment" --token "$VERCEL_TOKEN" --yes > /dev/null 2>&1
  set -e
  echo "$value" | vercel env add "$key" "$PROJECT_ID" "$environment" --token "$VERCEL_TOKEN" --yes
done < .env

echo "All done. Verify with: vercel env ls $PROJECT_ID --token $VERCEL_TOKEN"