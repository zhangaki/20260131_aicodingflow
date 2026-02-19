#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
BASE_URL="https://api3.adsterratools.com/publisher"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${ADSTERRA_API_KEY:-}" ]]; then
  echo "Missing ADSTERRA_API_KEY. Set it in $ENV_FILE" >&2
  exit 1
fi

usage() {
  cat <<'USAGE'
Usage:
  scripts/adsterra-api.sh domains
  scripts/adsterra-api.sh placements [domain_id]
  scripts/adsterra-api.sh stats --start YYYY-MM-DD --finish YYYY-MM-DD [--domain-id N] [--placement-id N] [--geo CC]

Examples:
  scripts/adsterra-api.sh domains
  scripts/adsterra-api.sh placements 1385226
  scripts/adsterra-api.sh stats --start 2026-02-01 --finish 2026-02-19 --domain-id 1385226
USAGE
}

api_get() {
  local endpoint="$1"
  curl -sS \
    -H "X-API-Key: $ADSTERRA_API_KEY" \
    "$BASE_URL/$endpoint"
}

build_query() {
  local first=1
  local pair
  for pair in "$@"; do
    [[ -z "$pair" ]] && continue
    if [[ $first -eq 1 ]]; then
      printf '?%s' "$pair"
      first=0
    else
      printf '&%s' "$pair"
    fi
  done
}

cmd="${1:-}"
shift || true

case "$cmd" in
  domains)
    api_get "domains.json"
    ;;
  placements)
    domain_id="${1:-}"
    if [[ -n "$domain_id" ]]; then
      api_get "domain/${domain_id}/placements.json"
    else
      api_get "placements.json"
    fi
    ;;
  stats)
    start=""
    finish=""
    domain_id=""
    placement_id=""
    geo=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --start)
          start="${2:-}"
          shift 2
          ;;
        --finish)
          finish="${2:-}"
          shift 2
          ;;
        --domain-id)
          domain_id="${2:-}"
          shift 2
          ;;
        --placement-id)
          placement_id="${2:-}"
          shift 2
          ;;
        --geo)
          geo="${2:-}"
          shift 2
          ;;
        *)
          echo "Unknown argument: $1" >&2
          usage
          exit 1
          ;;
      esac
    done

    if [[ -z "$start" || -z "$finish" ]]; then
      echo "stats requires --start and --finish" >&2
      usage
      exit 1
    fi

    # API currently expects domain/placement/country in query.
    query="$(build_query \
      "start_date=$start" \
      "finish_date=$finish" \
      "${domain_id:+domain=$domain_id}" \
      "${placement_id:+placement=$placement_id}" \
      "${geo:+country=$geo}")"
    api_get "stats.json${query}"
    ;;
  *)
    usage
    exit 1
    ;;
esac
