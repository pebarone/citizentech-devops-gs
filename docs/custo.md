# Estimativa de custo mensal

> **Valores aproximados, a confirmar.** Antes da entrega, refaça a conta na
> [Calculadora de Preços do Azure](https://azure.microsoft.com/pricing/calculator/), região **Chile Central**, e cole
> o print no PDF. Os preços mudam por região e por data.

O projeto roda numa assinatura **Azure for Students**: crédito de US$ 100, sem cartão de crédito cadastrado.
Quando o crédito acaba, os recursos são desligados; nada é cobrado da equipe. O desenho usa a cota gratuita
de 12 meses sempre que possível, então o crédito só paga o IP público.

| Recurso | SKU | Quantidade | Preço de tabela US$/mês | Custo real |
|---|---|---|---|---|
| Máquina virtual | Standard_B2ats_v2 (2 vCPU, 1 GiB), Linux | 730 h | ~7 | **0** (cota gratuita: 750 h/mês) |
| Disco do SO | Premium SSD P6, 64 GiB | 1 | ~10 | **0** (cota gratuita: 2 × P6) |
| IP público | Standard, estático | 1 | ~3,65 | **~3,65** (sai do crédito) |
| Storage do state | Standard LRS, menos de 1 MB | 1 | < 0,10 | **0** (cota gratuita: 5 GB) |
| Tráfego de saída | — | < 1 GB | 0 | **0** (100 GB/mês gratuitos) |
| Rede virtual, NSG, identidade gerenciada | — | — | 0 | **0** |
| GitHub Actions e GHCR | repositório público | — | 0 | **0** |
| Prometheus e Grafana | rodam na máquina da equipe | — | 0 | **0** |
| **Total** | | | **~21** | **~3,65** |

Um orçamento de US$ 5/mês (`budget_amount`) avisa por e-mail os Owners da assinatura em 80% do valor real
e em 100% do previsto.

## Por que Chile Central e não Brazil South

A assinatura Azure for Students só permite criar recursos em cinco regiões (política *Allowed resource
deployment regions*): Brazil South, Chile Central, Mexico Central, Spain Central e France Central. Brazil South
não oferece nenhum dos tamanhos da cota gratuita (B1s, B2ats_v2, B2pts_v2) para essa conta. Entre as demais,
Chile Central é a mais próxima do cidadão brasileiro e oferece o B2ats_v2. Ver o impacto para a LGPD em
[lgpd.md](lgpd.md).

## Como reduzir

- **Desalocar a VM fora da avaliação** (`az vm deallocate`): para a contagem de horas, mas o IP continua cobrando.
- `terraform destroy` depois da correção zera o custo, exceto o storage do state, que fica na cota gratuita.

## Se o MVP crescer

| Cenário | Mudança | Impacto |
|---|---|---|
| Dados no Brasil | `location = "brazilsouth"` com assinatura paga | VM e disco passam a ser cobrados (~US$ 20/mês) |
| Mais acessos | `vm_size = "Standard_B2s"` | Sai da cota gratuita (~US$ 30/mês) |
| Alta disponibilidade | 2 VMs + Load Balancer, ou migrar para Azure Container Apps | Exige estado externo (banco gerenciado) |
| Banco de dados | Azure Database for PostgreSQL Flexible (B1ms) | + ~US$ 15–25 |
