# Onde ficam os dados pessoais (LGPD)

> Cada dado pessoal novo do Alerta Córrego entra nesta tabela antes de ir para produção.

## Inventário

| Dado | Onde é coletado | Onde fica armazenado | Retenção | Base legal | Proteção |
|---|---|---|---|---|---|
| Endereço IP do visitante | Caddy (acesso HTTP) | Log do container na VM (`json-file`, 3 arquivos de 10 MB, rotativo) | Até a rotação (dias) | Legítimo interesse (segurança) | Disco criptografado pela Azure; acesso só por Run Command ou SSH restrito |
| Telefone celular do morador (fase seguinte, fora deste MVP) | Cadastro por SMS ou WhatsApp, com aceite explícito | Banco gerenciado na mesma região da VM, cifrado em repouso | Até o morador pedir o descadastro, ou 12 meses sem confirmar interesse | Consentimento (art. 7º, I) e proteção da vida (art. 7º, VII) | Cifrado em repouso, acesso só pelo robô de envio, nunca exibido na tela |
| Ponto de córrego escolhido pelo morador (fase seguinte) | Mesmo cadastro | Mesmo banco, ligado ao telefone | Igual ao telefone | Consentimento | Guardamos o ponto monitorado, nunca o endereço da casa |

## O que **não** guardamos

- As métricas do Prometheus não têm IP, usuário nem parâmetro de URL. A rota é registrada pelo template
  (`/api/v1/corregos/{ponto_id}`), nunca pelo valor.
- O repositório não tem dados pessoais reais. Dados de teste devem ser sintéticos.
- A tela pública não pede nome, telefone nem localização. As leituras dos córregos não são dados pessoais.

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
- **Transparência:** a tela do MVP informa que não coleta dado pessoal. O cadastro de telefone, quando existir,
  vai dizer para que serve e como sair.
