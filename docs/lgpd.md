# Onde ficam os dados pessoais (LGPD)

> Atualizar quando o produto da equipe estiver definido. Cada dado pessoal novo entra nesta tabela.

## Inventário

| Dado | Onde é coletado | Onde fica armazenado | Retenção | Base legal | Proteção |
|---|---|---|---|---|---|
| Endereço IP do visitante | Caddy (acesso HTTP) | Log do container na VM (`json-file`, 3 × 10 MB, rotativo) | Até a rotação (dias) | Legítimo interesse (segurança) | Disco criptografado pela Azure; acesso só por Run Command ou SSH restrito |
| _dados do produto_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ |

## O que **não** guardamos

- As métricas do Prometheus não têm IP, usuário nem parâmetro de URL. A rota é registrada pelo template
  (`/api/v1/itens/{id}`), nunca pelo valor.
- O repositório não tem dados pessoais reais. Dados de teste devem ser sintéticos.

## Localização e transferência

- A infraestrutura fica em **Chile Central (Santiago)**, porque a conta de estudante não oferece VM gratuita em
  Brazil South (ver [custo.md](custo.md)). Hoje o único dado pessoal tratado é o IP do visitante, nos logs rotativos.
- Isso é transferência internacional (LGPD, art. 33). Ela se apoia nas cláusulas contratuais da Microsoft para
  serviços de nuvem e na criptografia em repouso e em trânsito.
- **Em produção real com dados do cidadão**, a recomendação é mudar `location` para `brazilsouth` numa assinatura
  paga. O Terraform não muda além dessa variável.
- O GitHub (EUA) guarda só código e imagens de container, sem dados pessoais.

## Princípios aplicados

- **Minimização:** só coletamos o necessário para a funcionalidade.
- **Segurança:** TLS em todo o tráfego público, segredos fora do código e acesso administrativo restrito.
- **Transparência:** a tela do MVP deve informar o que é coletado e por quê.
