# Roteiro de evidências para o PDF

Cada print precisa de legenda. Tire os prints nesta ordem, que segue a rubrica.

## Container e IaC (5,0)

- [ ] `docker compose up -d --build` subindo a stack, e `docker compose ps` com a API `healthy`.
- [ ] `docker run --rm --entrypoint id <imagem>` mostrando `uid=10001`, ou seja, não root.
- [ ] `docker history <imagem>` ou `docker image ls` mostrando o tamanho enxuto.
- [ ] `terraform apply` concluído, com os outputs.
- [ ] Portal Azure → NSG → regras de entrada: só 80/443 da Internet e 22 restrito, ou sem regra 22.
- [ ] `terraform plan` com `admin_cidrs = ["0.0.0.0/0"]` sendo **rejeitado** pela validação.
- [ ] `git ls-files | grep -E "tfstate|tfvars|backend.hcl|tfplan" | grep -v '\.example$'` sem resultado, e o state no container do Storage Account.

## Pipeline DevSecOps (4,0)

- [ ] Uma execução verde com todos os jobs: Gitleaks, Semgrep, Testes, Terraform, Build + Trivy e Deploy.
- [ ] Settings → Environments → `production`, com os nomes dos secrets visíveis e os valores ocultos.
- [ ] O job Deploy com `deploy ok` e o smoke test confirmando o SHA na URL pública.

### Execução barrada e corrigida

Faça numa branch, por exemplo `demo/pipeline-barrado`, para não sujar a `main`. Use só valores **falsos**.

1. **Segredo vazado (Gitleaks).** Crie `app/citizentech/demo_leak.py` com uma chave de exemplo no formato
   AWS, por exemplo `AWS_ACCESS_KEY_ID = "AKIA" + 16 caracteres maiúsculos e números aleatórios`. Faça commit e push.
   O job **Segredos (Gitleaks)** fica vermelho e o build e o deploy nem começam. Tire o print.
2. **Correção.** Apague o arquivo, faça commit e push. Agora a execução fica verde. Tire o print.
3. **Opcional, vulnerabilidade (Trivy).** Troque `fastapi` em `app/requirements.txt` por uma versão
   antiga com CVE conhecida. O Trivy barra a imagem. Volte a versão e mostre o verde.

Por ser falso, o segredo de demonstração não precisa ser revogado. Um segredo real precisaria.

**Não faça merge nem abra PR da branch de demonstração, e apague-a depois.** Num PR ou num
`workflow_dispatch`, o Gitleaks varre o histórico inteiro, encontra a chave falsa e o pipeline volta a ficar vermelho.

## Observabilidade (3,0)

- [ ] O dashboard **Alerta Córrego: 4 sinais de ouro** com dados de produção: latência, tráfego, erros e saturação.
- [ ] O Prometheus em `/targets` com `citizentech-prod` UP.
- [ ] **Alerta disparado.** Escolha uma opção:
  - **MVPForaDoAr:** pare a API na VM com Run Command ou SSH, rodando
    `docker compose -f /opt/citizentech/docker-compose.prod.yml stop api`. Depois de cerca de 1 min o alerta
    fica FIRING. Suba a API de novo.
  - **TaxaDeErroAlta:** ligue o modo chaos na VM:

    ```bash
    az vm run-command invoke -g <rg> -n <vm> --command-id RunShellScript --scripts \
      "cd /opt/citizentech && sed -i 's/^ENABLE_CHAOS=.*/ENABLE_CHAOS=true/' .env && docker compose -f docker-compose.prod.yml up -d"
    ```

    Gere erros com `for i in $(seq 200); do curl -s $MVP_URL/api/v1/chaos/error >/dev/null; done`.
    Depois rode o mesmo comando com `ENABLE_CHAOS=false`.
- [ ] O print do Prometheus em `/alerts` e do Alertmanager com o alerta FIRING.

## Documentação (2,0)

- [ ] O diagrama de [arquitetura.md](arquitetura.md). Exporte o Mermaid em https://mermaid.live.
- [ ] [responsabilidade-compartilhada.md](responsabilidade-compartilhada.md), [lgpd.md](lgpd.md) e [custo.md](custo.md), com o print da calculadora.
- [ ] O README com a Ficha Técnica preenchida.
