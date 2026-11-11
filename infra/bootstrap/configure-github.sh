#!/usr/bin/env bash
# Cadastra no GitHub os secrets e variáveis do deploy a partir do "terraform output".
# Pré-requisitos: terraform apply concluído, gh auth login, jq.
# Uso (na raiz do repositório): bash infra/bootstrap/configure-github.sh
set -euo pipefail

TF_DIR="$(dirname "$0")/../terraform"
OUT=$(terraform -chdir="$TF_DIR" output -json github_actions_settings)
get() { echo "$OUT" | jq -er ".value.$1 // .$1"; }

# O environment precisa existir antes de receber secrets.
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh api --method PUT "repos/$REPO/environments/production" >/dev/null

for s in AZURE_CLIENT_ID AZURE_TENANT_ID AZURE_SUBSCRIPTION_ID; do
  get "$s" | gh secret set "$s" --env production --repo "$REPO"
done

for v in AZURE_RESOURCE_GROUP AZURE_VM_NAME MVP_URL; do
  gh variable set "$v" --body "$(get "$v")" --repo "$REPO"
done

echo "GitHub configurado para $REPO. O próximo push na main faz o deploy."
