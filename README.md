# Alerta Córrego

> Global Solution 2026.2, FIAP, Engenharia de Software 4º ano.
> Disciplina **Secure DevOps Tools & Cloud Computing**, componente **Produção** (atividade Deploy Blindado).

O Alerta Córrego avisa quem mora na beira de córrego que a água está subindo, antes de ela chegar à porta.
Este repositório coloca o MVP no ar sem clique em botão: container, nuvem descrita em Terraform e um pipeline
que barra segredo vazado e vulnerabilidade antes de qualquer coisa chegar ao cidadão.

**URL do MVP:** https://citizentech-afvgwa.chilecentral.cloudapp.azure.com

**Repositório:** https://github.com/pebarone/citizentech-devops-gs

## Integrantes

| Nome completo | RM |
|---|---|
| João Pedro de Albuquerque Oliveira | 551579 |
| Pedro Augusto Carneiro Barone Bomfim | 99781 |
| Matheus Augusto Santos Rego | 551466 |

## Ficha Técnica do MVP

| Campo | Resposta |
|---|---|
| Nome do produto | Alerta Córrego |
| Cidadão e território | Famílias que moram em áreas de alagamento na beira de córregos da Zona Leste de São Paulo: Jardim Pantanal, Jardim Romano, Jardim Helena e Guaianases. Muitas usam celular de entrada e internet instável. |
| Problema, em uma frase | Quem mora perto do córrego descobre a enchente quando a água já entrou em casa, porque o alerta oficial vale para a cidade inteira e não diz o que acontece naquela rua. |
| Proposta de valor | Aviso por ponto de córrego, com minutos de antecedência, a partir de sensores baratos instalados na margem, e uma orientação curta do que fazer em cada nível de risco. Chega pela web, por SMS e por WhatsApp, e funciona em celular simples. |
| Arquitetura: componentes | **Dispositivo:** sensor ultrassônico em ESP32 mede o nível do córrego e envia a leitura. **Dados:** Airflow coleta chuva e nível, Databricks trata em Bronze, Prata e Ouro. **Visão:** câmeras na margem confirmam o nível por imagem. **Inteligência:** LLM local responde dúvidas do morador com base nos protocolos da Defesa Civil. **Automação:** robô RPA dispara SMS e WhatsApp para os moradores cadastrados no ponto em risco. **Produção:** API FastAPI em container, numa VM Azure criada por Terraform, com pipeline DevSecOps no GitHub Actions e observabilidade em Prometheus e Grafana ([arquitetura](docs/arquitetura.md)). **Negócio:** painel para subprefeituras e Defesa Civil. |
| Fontes de dados | Pluviômetros automáticos do CEMADEN (dados abertos), boletins e alertas do CGE da Prefeitura de São Paulo, estações do INMET, mapa de áreas de risco e hidrografia do GeoSampa e leituras dos sensores próprios. Nesta versão do MVP as leituras dos quatro pontos são simuladas por uma função determinística, documentada em [corregos.py](app/citizentech/corregos.py). |
| Modelos de IA utilizados | Modelo de regressão (gradient boosting) que prevê o nível do córrego nos próximos 30 minutos a partir da chuva e do nível atual. Modelo de detecção de objetos (YOLO) que lê a régua de nível nas imagens das câmeras. LLM local de pequeno porte, ajustado com QLoRA e consultando uma base com os protocolos da Defesa Civil, para orientar o morador em linguagem simples. |
| URL do MVP e repositório | https://citizentech-afvgwa.chilecentral.cloudapp.azure.com e https://github.com/pebarone/citizentech-devops-gs |
| Indicadores de impacto | Antecedência média do alerta antes do transbordo, com meta de 30 minutos. Percentual de moradores cadastrados que recebem o aviso em até 5 minutos. Taxa de alarme falso, com meta abaixo de 10%. Famílias cadastradas por ponto monitorado. Perdas materiais relatadas pelos moradores antes e depois da instalação. |
| ODS conectados | **ODS 11** (meta 11.5): reduz perdas e mortes causadas por desastres ligados à água, com foco em quem mora em área vulnerável. **ODS 13** (meta 13.1): aumenta a capacidade de adaptação da comunidade a chuvas extremas. **ODS 10** (meta 10.2): leva alerta de qualidade a bairros da periferia, que hoje recebem só o aviso genérico. |

## O MVP no ar

A página inicial mostra os quatro pontos monitorados, com nível da água, chuva na última hora, nível de risco
(Normal, Atenção, Alerta ou Emergência) e o que o morador deve fazer. Os telefones da Defesa Civil (199) e dos
Bombeiros (193) ficam sempre visíveis. A página não coleta dado pessoal.

| Rota | O que faz |
|---|---|
| `/` | Tela do cidadão |
| `/api/v1/corregos` | Leituras dos quatro pontos |
| `/api/v1/corregos/{ponto_id}` | Leitura de um ponto |
| `/api/v1/info` | Nome, ambiente e versão implantada (SHA do commit) |
| `/healthz` e `/readyz` | Saúde do processo |
| `/metrics` | Métricas Prometheus, só com token Bearer |

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

Repositórios novos do GitHub emitem o token OIDC com IDs imutáveis. Preencha também `github_oidc_subject_prefix`
com a saída de `gh api repos/<owner>/<repo>/actions/oidc/customization/sub --jq .sub_claim_prefix`. Sem isso, o
login na Azure falha com `AADSTS700213`.

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

O Grafana fica em http://localhost:3000, com o dashboard **Alerta Córrego: 4 sinais de ouro**. O Prometheus
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
