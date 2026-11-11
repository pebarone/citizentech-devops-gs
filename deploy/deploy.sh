#!/usr/bin/env bash
# Executado DENTRO da VM via "az vm run-command invoke" pelo GitHub Actions.
# Nenhuma porta de administração é aberta para o runner: o comando entra pelo plano de controle do Azure.
#
# Uso: deploy.sh <repo owner/name> <commit sha> <imagem completa>
set -euo pipefail

REPO="$1"
SHA="$2"
IMAGE="$3"
DIR=/opt/citizentech
COMPOSE=(docker compose -f docker-compose.prod.yml)

# Numa VM recém-criada, o cloud-init pode ainda estar instalando o Docker.
cloud-init status --wait >/dev/null 2>&1 || true

cd "$DIR"

fail() {
  echo "$1" >&2
  "${COMPOSE[@]}" logs --tail 50 api >&2 || true
  exit 1
}

# Baixa os arquivos da stack exatamente na versão do commit implantado.
caddy_before=$(sha256sum Caddyfile 2>/dev/null | cut -d' ' -f1 || true)
for f in docker-compose.prod.yml Caddyfile; do
  curl -fsSL --retry 3 -o "$f.new" "https://raw.githubusercontent.com/${REPO}/${SHA}/deploy/${f}"
  mv "$f.new" "$f"
done
caddy_after=$(sha256sum Caddyfile | cut -d' ' -f1)

# Grava a versão implantada no .env (gerado pelo cloud-init, permissão 600). O compose lê o .env
# automaticamente, então comandos manuais depois do deploy (stop/up) continuam funcionando.
upsert() {
  if grep -q "^$1=" .env; then sed -i "s|^$1=.*|$1=$2|" .env; else echo "$1=$2" >> .env; fi
}
upsert API_IMAGE "$IMAGE"
upsert APP_VERSION "$SHA"

"${COMPOSE[@]}" pull || fail "falha ao baixar as imagens"
# O proxy depende da API saudável (depends_on: service_healthy), então o "up" já espera o healthcheck.
"${COMPOSE[@]}" up -d --remove-orphans || fail "a stack não subiu (API não ficou saudável?)"

# O bind mount do Caddyfile aponta para o arquivo antigo depois do mv: recria o proxy se ele mudou.
if [ "$caddy_before" != "$caddy_after" ]; then
  "${COMPOSE[@]}" up -d --force-recreate --no-deps proxy || fail "falha ao recriar o proxy"
fi

status=$(docker inspect --format '{{.State.Health.Status}}' "$("${COMPOSE[@]}" ps -q api)" 2>/dev/null || echo unknown)
[ "$status" = "healthy" ] || fail "API em estado '$status' depois do deploy"

docker image prune -f >/dev/null || true
echo "deploy ok: $IMAGE"
