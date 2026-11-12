# Estimativa de custo mensal

Valores da [Calculadora de Preços do Azure](https://azure.microsoft.com/pricing/calculator/), consultada em
12/11/2026, região **Chile Central**, preço pago conforme o uso, em dólar. Os prints estão em
[evidencias/](evidencias/) (`calc-*.png`).

O projeto roda numa assinatura **Azure for Students**: crédito de US$ 100, sem cartão de crédito cadastrado e
com limite de gastos ligado. Quando o crédito acaba, os recursos são desligados e nada é cobrado da equipe. O
desenho usa a cota gratuita de 12 meses da conta de estudante, então o crédito paga só o IP público.

| Recurso | Configuração | Preço de tabela (US$/mês) | Custo real (US$/mês) |
|---|---|---:|---:|
| Máquina virtual | Standard_B2ats_v2 (2 vCPU, 1 GiB), Ubuntu, 730 h | 9,64 | **0,00**, cota gratuita de 750 h/mês |
| Disco do sistema | Premium SSD P6, 64 GiB, LRS | 13,02 | **0,00**, cota gratuita de 2 discos P6 |
| IP público | Standard, estático, 730 h | 3,65 | **3,65**, sai do crédito de estudante |
| **Total na calculadora** | | **26,31** | **3,65** |

Itens que não entram na calculadora porque custam zero neste projeto:

| Item | Por que não custa |
|---|---|
| Storage Account do state do Terraform | Menos de 1 MB, dentro da cota gratuita de 5 GB |
| Tráfego de saída | Menos de 1 GB por mês, e os primeiros 100 GB são gratuitos |
| Rede virtual, NSG e identidade gerenciada | Sem cobrança na Azure |
| GitHub Actions e GHCR | Repositório público |
| Prometheus, Alertmanager e Grafana | Rodam na máquina da equipe |

Um orçamento de US$ 5 por mês (`budget_amount` no Terraform) avisa por e-mail os donos da assinatura quando o
gasto real passa de 80% ou quando a previsão passa de 100%.

## Por que Chile Central e não Brazil South

A assinatura Azure for Students só permite criar recursos em cinco regiões (política *Allowed resource
deployment regions*): Brazil South, Chile Central, Mexico Central, Spain Central e France Central. Em Brazil
South, essa conta não oferece nenhum dos tamanhos de VM da cota gratuita (B1s, B2ats_v2, B2pts_v2). Entre as
outras, Chile Central é a mais próxima do cidadão brasileiro e oferece o B2ats_v2. O impacto para a LGPD está
em [lgpd.md](lgpd.md).

## Como reduzir

- **Desalocar a VM fora da avaliação** (`az vm deallocate`): para a contagem de horas, mas o IP continua cobrando.
- **`terraform destroy` depois da correção**: zera o custo. Só o storage do state fica, dentro da cota gratuita.

## Se o MVP crescer

| Cenário | Mudança | Impacto |
|---|---|---|
| Dados no Brasil | `location = "brazilsouth"` numa assinatura paga | VM e disco passam a ser cobrados, cerca de US$ 25 por mês |
| Mais acessos | `vm_size = "Standard_B2s"` | Sai da cota gratuita, cerca de US$ 30 por mês só de VM |
| Alta disponibilidade | Duas VMs com Load Balancer, ou migração para Azure Container Apps | Exige estado fora da VM, como um banco gerenciado |
| Banco de dados | Azure Database for PostgreSQL Flexible (B1ms) | Mais US$ 15 a 25 por mês |
