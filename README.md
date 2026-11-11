# CitizenTech MVP — Deploy Blindado

> Global Solution 2026.2 · FIAP · Engenharia de Software 4º ano
> Disciplina **Secure DevOps Tools & Cloud Computing** — componente **Produção**

O MVP da equipe vai para o ar sem clique em botão: container, nuvem descrita em Terraform e um
pipeline que barra segredo vazado e vulnerabilidade antes de qualquer coisa chegar ao cidadão.

**URL do MVP:** https://citizentech-afvgwa.chilecentral.cloudapp.azure.com

## Integrantes

| Nome completo | RM |
|---|---|
| _preencher_ | _preencher_ |

## Ficha Técnica do MVP

| Campo | Resposta |
|---|---|
| Nome do produto | _preencher_ |
| Cidadão e território | _preencher_ |
| Problema, em uma frase | _preencher_ |
| Proposta de valor | _preencher_ |
| Arquitetura: componentes | API FastAPI em container → Caddy (HTTPS) → VM Azure (Chile Central, cota gratuita) criada por Terraform; CI/CD DevSecOps no GitHub Actions; observabilidade Prometheus + Grafana. Ver [docs/arquitetura.md](docs/arquitetura.md). _Completar com os componentes das outras disciplinas._ |
| Fontes de dados | _preencher (componente Dados)_ |
| Modelos de IA utilizados | _preencher (componentes Inteligência e Visão)_ |
| URL do MVP e repositório | https://citizentech-afvgwa.chilecentral.cloudapp.azure.com · https://github.com/pebarone/citizentech-devops-gs |
| Indicadores de impacto | _preencher_ |
| ODS conectados | _preencher (obrigatório)_ |

## Como este repositório atende a avaliação (14 pontos)

| Critério | Onde está |
|---|---|
| Dockerfile enxuto, não root, sem segredo | [app/Dockerfile](app/Dockerfile): multi-stage, `USER 10001`, `HEALTHCHECK`, [.dockerignore](app/.dockerignore) |
| Stack com docker compose | [docker-compose.yml](docker-compose.yml) (local) e [deploy/docker-compose.prod.yml](deploy/docker-compose.prod.yml) (VM) |
| Nuvem por Terraform | [infra/terraform/](infra/terraform/) |
| State e .tfvars fora do repo | backend `azurerm` remoto ([bootstrap](infra/bootstrap/create-tfstate-storage.sh)); `*.tfvars`, `backend.hcl` e `*.tfstate` no [.gitignore](.gitignore) |
| Porta admin nunca em 0.0.0.0/0 | SSH só para `admin_cidrs`, com `validation` que rejeita 0.0.0.0/0 ([variables.tf](infra/terraform/variables.tf)); o deploy usa o Run Command do Azure, sem SSH |
| Build, Gitleaks, Semgrep e Trivy a cada push | [.github/workflows/devsecops.yml](.github/workflows/devsecops.yml) |
| Segredos em GitHub Secrets | login na Azure por OIDC, sem senha guardada; IDs nos secrets do environment `production` |
| Deploy automático | job `deploy`: push na `main` → GHCR → VM → smoke test na URL pública |
| Execução barrada e corrigida | roteiro em [docs/evidencias.md](docs/evidencias.md#execução-barrada-e-corrigida) |
| 4 sinais de ouro + alerta | [observability/](observability/): dashboard provisionado e regras em [alerts.yml](observability/prometheus/alerts.yml) |
| Diagrama, responsabilidade compartilhada, LGPD, custo | [docs/](docs/) |

## Estrutura

```
app/                     API FastAPI, testes e Dockerfile
deploy/                  compose de produção, Caddyfile e script de deploy (roda na VM)
infra/bootstrap/         cria o storage do state remoto (uma vez)
infra/terraform/         rede, NSG, IP público, VM e identidade OIDC do GitHub
observability/           Prometheus, Alertmanager e Grafana (rodam local)
docs/                    arquitetura, LGPD, custo, responsabilidade e evidências
.github/workflows/       pipeline DevSecOps
```

## Rodar localmente

Pré-requisito: Docker com Compose v2.

```bash
docker compose up -d --build
```

- MVP: http://localhost:8080
- Métricas: http://localhost:8000/metrics

Testes sem Docker (Python 3.12):

```bash
cd app && pip install -r requirements-dev.txt && pytest -q
```

## Colocar na nuvem (Azure)

Pré-requisitos: [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), Terraform 1.6 ou mais recente,
uma chave SSH e o repositório já publicado no GitHub como **público**. O enunciado exige isso, e a VM baixa o
compose e o script de deploy direto do GitHub, sem credencial.

**1. State remoto, uma vez só**

```bash
az login
bash infra/bootstrap/create-tfstate-storage.sh
```

Grave a saída em `infra/terraform/backend.hcl`. O modelo está em [backend.hcl.example](infra/terraform/backend.hcl.example).

**2. Variáveis**

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```

Preencha `subscription_id`, `github_repository`, `admin_ssh_public_key` e `metrics_token`
(`openssl rand -hex 32`). O arquivo é ignorado pelo git.

**3. Infraestrutura**

```bash
cd infra/terraform
terraform init -backend-config=backend.hcl
terraform plan -out=tfplan
terraform apply tfplan
terraform output github_actions_settings
```

**4. GitHub**

| Onde | Tipo | Nome | Valor |
|---|---|---|---|
| Environment `production` | Secret | `AZURE_CLIENT_ID` | da saída do Terraform |
| Environment `production` | Secret | `AZURE_TENANT_ID` | da saída do Terraform |
| Environment `production` | Secret | `AZURE_SUBSCRIPTION_ID` | da saída do Terraform |
| Repositório | Variable | `AZURE_RESOURCE_GROUP` | da saída do Terraform |
| Repositório | Variable | `AZURE_VM_NAME` | da saída do Terraform |
| Repositório | Variable | `MVP_URL` | da saída do Terraform |

As variáveis ficam no repositório porque o `if` do job de deploy lê `AZURE_VM_NAME`, e um job não enxerga
as variáveis do environment antes de começar. Enquanto `AZURE_VM_NAME` não existir, o deploy é pulado.
Com o `gh` autenticado, `bash infra/bootstrap/configure-github.sh` cadastra tudo a partir do `terraform output`.

**5. Primeiro deploy.** Faça push na `main`. Depois que o primeiro build publicar a imagem, torne o pacote
`api` público em GitHub → Packages → Package settings → Change visibility. A VM baixa a imagem sem credencial.
Se o deploy tiver falhado por isso, rode o workflow de novo.

**6. Observabilidade**

```bash
cp observability/.env.example observability/.env        # defina a senha do Grafana
echo -n "<metrics_token>" > observability/secrets/metrics_token
# edite observability/prometheus/targets/prod.yml com o FQDN do MVP
docker compose -f observability/docker-compose.yml up -d
```

O Grafana fica em http://localhost:3000, com o dashboard **CitizenTech - 4 sinais de ouro**. O Prometheus
fica em http://localhost:9090/alerts.

**Para derrubar tudo e parar o custo:** `terraform destroy`.

## Segurança

- Nenhuma credencial no código. A configuração vem de variáveis de ambiente. Na VM, o `.env` com
  permissão 600 é gerado pelo cloud-init.
- `/metrics` exige token Bearer em produção. `/docs` e `/openapi.json` ficam desligados em produção.
- O container roda sem root, com sistema de arquivos somente leitura, `cap_drop: ALL` e `no-new-privileges`.
- O deploy usa uma identidade federada (OIDC) com o papel `Virtual Machine Contributor` restrito à VM.
- Se um segredo real vazar, revogue-o. O pipeline volta ao verde depois do commit de correção, mas o
  segredo continua no histórico do git.
