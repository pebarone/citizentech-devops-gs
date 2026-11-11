#!/usr/bin/env bash
# Cria (uma única vez) a Storage Account que guarda o state do Terraform fora do repositório.
# Pré-requisito: az login
# Uso: ./create-tfstate-storage.sh [regiao]
set -euo pipefail

LOCATION="${1:-brazilsouth}"
RG="rg-citizentech-tfstate"
SA="sttfstate$(openssl rand -hex 3)"
CONTAINER="tfstate"

az group create --name "$RG" --location "$LOCATION" --output none

az storage account create \
  --name "$SA" \
  --resource-group "$RG" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false \
  --allow-shared-key-access false \
  --output none

# Versionamento permite recuperar um state corrompido.
az storage account blob-service-properties update \
  --account-name "$SA" --resource-group "$RG" \
  --enable-versioning true --output none

# Quem roda o Terraform precisa do papel de dados no blob (auth via Entra ID, sem chave).
ME=$(az ad signed-in-user show --query id -o tsv)
SCOPE=$(az storage account show --name "$SA" --resource-group "$RG" --query id -o tsv)
az role assignment create --assignee "$ME" --role "Storage Blob Data Contributor" --scope "$SCOPE" --output none

# A atribuição de papel leva alguns segundos para propagar.
created=false
for i in $(seq 1 12); do
  if az storage container create --name "$CONTAINER" --account-name "$SA" --auth-mode login --output none 2>/dev/null; then
    created=true; break
  fi
  sleep 10
done
if [ "$created" != true ]; then
  echo "Não foi possível criar o container '$CONTAINER' em $SA. Rode de novo em alguns minutos." >&2
  exit 1
fi

cat <<EOF

State remoto pronto. Grave em infra/terraform/backend.hcl:

resource_group_name  = "$RG"
storage_account_name = "$SA"
container_name       = "$CONTAINER"
key                  = "citizentech/prod.tfstate"
use_azuread_auth     = true
EOF
