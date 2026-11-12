# Responsabilidade compartilhada

Neste projeto usamos **IaaS**: uma VM. Nesse modelo, a parte que cabe à equipe é maior do que em PaaS ou SaaS.

| Camada | Microsoft Azure | Equipe | Como a equipe cumpre |
|---|:-:|:-:|---|
| Datacenter, energia e rede física | ✅ | | Responsabilidade da Microsoft |
| Hipervisor e hardware | ✅ | | Responsabilidade da Microsoft |
| Rede virtual e regras de firewall (NSG) | plataforma | ✅ regras | NSG em Terraform: só 80/443 públicos e SSH restrito por `admin_cidrs` |
| Sistema operacional da VM | imagem base | ✅ patches | `package_upgrade` e `unattended-upgrades` no cloud-init |
| Runtime de containers (Docker) | | ✅ | Instalado pelo cloud-init. O `unattended-upgrades` só aplica as atualizações de segurança do Ubuntu, então o Docker é atualizado manualmente com `apt-get upgrade` |
| Imagem da aplicação | | ✅ | Dockerfile multi-stage, não root, scan Trivy a cada push |
| Código da aplicação | | ✅ | Semgrep, testes e revisão por PR |
| Segredos | Key Vault/Entra (serviço) | ✅ uso | OIDC no deploy, `.env` 600 na VM, GitHub Secrets e nada no repo (Gitleaks) |
| Identidade e acesso | Entra ID (serviço) | ✅ papéis | Identidade de deploy com papel mínimo, restrito à VM |
| Dados e LGPD | criptografia em repouso do disco | ✅ classificação e minimização | Ver [lgpd.md](lgpd.md) |
| Monitoramento da aplicação | | ✅ | Prometheus, Grafana e alertas dos 4 sinais de ouro |
| Backup e recuperação | snapshots (serviço) | ✅ política | State versionado; a infra é recriada por `terraform apply` |
