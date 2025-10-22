#!/usr/bin/env bash
set -euo pipefail
ALLOWED_PATHS_FILE="${1:-allowed_paths.txt}"
CHANGED=$(git diff --name-only --cached || true)

if [[ ! -f "$ALLOWED_PATHS_FILE" ]]; then
  echo "allowed_paths.txt not found"; exit 1
fi

violations=0
while IFS= read -r file; do
  allowed=0
  while IFS= read -r pattern; do
    [[ -z "$pattern" ]] && continue
    if [[ "$file" == $pattern* ]]; then
      allowed=1; break
    fi
  done < "$ALLOWED_PATHS_FILE"
  if [[ $allowed -eq 0 ]]; then
    echo "❌ Disallowed change: $file"
    violations=$((violations+1))
  fi
done <<< "$CHANGED"

if [[ $violations -gt 0 ]]; then
  echo "Aborting commit. Edit allowed_paths.txt or move files accordingly."
  exit 2
fi
echo "✅ Scope check passed."
