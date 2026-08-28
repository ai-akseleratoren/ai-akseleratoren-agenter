#!/usr/bin/env bash
# Inviterer medlemmer til GitHub-organisasjonen som read-only på agentbiblioteket.
#
# FØRST, én gang:
#   gh auth refresh -s admin:org
#
# BRUK:
#   ./inviter-medlemmer.sh medlemmer.txt          # tørrkjøring, viser hva som skjer
#   ./inviter-medlemmer.sh medlemmer.txt --send   # sender faktisk
#
# medlemmer.txt: én e-postadresse per linje. Tomme linjer og # ignoreres.

set -euo pipefail

ORG="${ORG:-ai-akseleratoren}"
TEAM="${TEAM:-medlemmer}"
FIL="${1:-}"
SEND="${2:-}"

if [[ -z "$FIL" || ! -f "$FIL" ]]; then
  echo "Bruk: $0 <fil-med-eposter> [--send]" >&2
  exit 1
fi

if ! gh auth status 2>&1 | grep -q "admin:org"; then
  echo "MANGLER TILGANG: kjør først  gh auth refresh -s admin:org" >&2
  exit 1
fi

# Hent team-id (opprett teamet i GitHub-UI først hvis det ikke finnes)
TEAM_ID=$(gh api "orgs/$ORG/teams/$TEAM" --jq '.id' 2>/dev/null || echo "")
if [[ -z "$TEAM_ID" ]]; then
  echo "Fant ikke teamet '$TEAM' i '$ORG'." >&2
  echo "Opprett det på https://github.com/orgs/$ORG/new-team og gi det lesetilgang til repoet." >&2
  exit 1
fi

ok=0; feil=0; hoppet=0

while IFS= read -r epost || [[ -n "$epost" ]]; do
  epost="$(echo "$epost" | tr -d '[:space:]')"
  [[ -z "$epost" || "$epost" == \#* ]] && continue
  if [[ ! "$epost" =~ ^[^@]+@[^@]+\.[^@]+$ ]]; then
    echo "HOPPET OVER (ugyldig): $epost"; hoppet=$((hoppet+1)); continue
  fi

  if [[ "$SEND" != "--send" ]]; then
    echo "[tørrkjøring] ville invitert: $epost"
    ok=$((ok+1))
    continue
  fi

  if gh api "orgs/$ORG/invitations" -X POST \
       -f email="$epost" \
       -f role=direct_member \
       -F "team_ids[]=$TEAM_ID" >/dev/null 2>&1; then
    echo "INVITERT: $epost"; ok=$((ok+1))
  else
    echo "FEILET:   $epost"; feil=$((feil+1))
  fi
  sleep 1   # ponytail: 1s mellom kall holder oss under GitHubs rategrense
done < "$FIL"

echo
echo "Ferdig. OK: $ok  Feilet: $feil  Hoppet over: $hoppet"
[[ "$SEND" != "--send" ]] && echo "Dette var en tørrkjøring. Kjør med --send for å sende på ekte."
