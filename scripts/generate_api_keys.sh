#!/usr/bin/env bash
set -euo pipefail

KEY_COUNT="${KEY_COUNT:-10}"
KEY_BYTES="${KEY_BYTES:-32}"
ENV_FILE=""

usage() {
  cat <<'EOF'
Usage:
  source scripts/generate_api_keys.sh
  scripts/generate_api_keys.sh --env-file .env

Environment:
  KEY_COUNT  Number of keys to generate. Default: 10
  KEY_BYTES  Random bytes per key. Default: 32
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file)
      ENV_FILE="${2:-}"
      if [[ -z "$ENV_FILE" ]]; then
        echo "Missing value for --env-file" >&2
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      return 0 2>/dev/null || exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

API_KEYS="$(
  python3 - "$KEY_COUNT" "$KEY_BYTES" <<'PY'
import secrets
import sys

count = int(sys.argv[1])
bytes_count = int(sys.argv[2])

keys = [secrets.token_urlsafe(bytes_count) for _ in range(count)]
print(",".join(keys))
PY
)"

export API_KEYS

echo "Generated ${KEY_COUNT} API keys."

if [[ -n "$ENV_FILE" ]]; then
  umask 077
  printf 'API_KEYS=%s\n' "$API_KEYS" > "$ENV_FILE"
  echo "Saved API_KEYS to ${ENV_FILE}"
else
  echo "API_KEYS=${API_KEYS}"
fi

if [[ -z "$ENV_FILE" ]] && ! (return 0 2>/dev/null); then
  echo
  echo "This script was executed in a child shell."
  echo "Run it with source to keep API_KEYS in your current shell:"
  echo "source scripts/generate_api_keys.sh"
fi
