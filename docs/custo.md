# Estimativa de custo mensal

> **Valores aproximados, a confirmar.** Antes da entrega, refaça a conta na
> [Calculadora de Preços do Azure](https://azure.microsoft.com/pricing/calculator/), região **Brazil South**, e cole
> o print no PDF. Os preços mudam por região e por data.

| Recurso | SKU | Quantidade | US$/mês (aprox.) |
|---|---|---|---|
| Máquina virtual | Standard_B1s (1 vCPU, 1 GiB), Linux | 730 h | ~12 |
| Disco do SO | Standard HDD (S4, 32 GiB) | 1 | ~2 |
| IP público | Standard, estático | 1 | ~4 |
| Storage do state | Standard LRS, menos de 1 MB | 1 | < 0,10 |
| Tráfego de saída | primeiros 100 GB/mês gratuitos | — | 0 |
| GitHub Actions e GHCR | repositório público | — | 0 |
| Prometheus e Grafana | rodam na máquina da equipe | — | 0 |
| **Total** | | | **~18** |

## Como reduzir

- **Desalocar a VM fora da avaliação** (`az vm deallocate`): para a cobrança de computação, mas o IP e o disco continuam cobrando.
- `terraform destroy` depois da correção zera o custo, exceto o storage do state.
- Com o crédito do **Azure for Students** (US$ 100), o projeto fica no ar por vários meses.

## Se o MVP crescer

| Cenário | Mudança | Impacto |
|---|---|---|
| Mais acessos | `vm_size = "Standard_B2s"` | ~2× o custo da VM |
| Alta disponibilidade | 2 VMs + Load Balancer, ou migrar para Azure Container Apps | Exige estado externo (banco gerenciado) |
| Banco de dados | Azure Database for PostgreSQL Flexible (B1ms) | + ~US$ 15–25 |
