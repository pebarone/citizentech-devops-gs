variable "subscription_id" {
  description = "ID da assinatura Azure."
  type        = string
}

variable "project" {
  description = "Prefixo dos recursos."
  type        = string
  default     = "citizentech"
}

variable "location" {
  description = "Região Azure. Brazil South mantém os dados no Brasil (LGPD)."
  type        = string
  default     = "brazilsouth"
}

variable "vm_size" {
  description = "Tamanho da VM. B1s/B2s cabem no crédito do Azure for Students."
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Usuário administrador da VM (login só por chave SSH)."
  type        = string
  default     = "azureuser"
}

variable "admin_ssh_public_key" {
  description = "Chave pública SSH do administrador (conteúdo do .pub)."
  type        = string
}

variable "admin_cidrs" {
  description = <<-EOT
    CIDRs autorizados a acessar a porta de administração (SSH 22), ex.: ["200.100.50.25/32"].
    Lista vazia = nenhuma regra de SSH (acesso só pelo Run Command do Azure).
    0.0.0.0/0 e equivalentes são rejeitados.
  EOT
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for c in var.admin_cidrs :
      try(cidrhost(c, 0) != "" && tonumber(split("/", c)[1]) >= 8, false) && !contains(["0.0.0.0/0", "::/0", "*", "Internet", "Any"], c)
    ])
    error_message = "admin_cidrs deve conter apenas CIDRs específicos (prefixo /8 ou maior). A porta de administração nunca pode ficar aberta para 0.0.0.0/0."
  }
}

variable "github_repository" {
  description = "Repositório GitHub no formato owner/nome, autorizado a fazer deploy via OIDC. Diferencia maiúsculas: copie exatamente como aparece no GitHub."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "Use o formato owner/nome."
  }
}

variable "github_environment" {
  description = "Environment do GitHub Actions que pode fazer deploy (o subject do token OIDC)."
  type        = string
  default     = "production"
}

variable "metrics_token" {
  description = "Token Bearer exigido em /metrics. Gere com: openssl rand -hex 32"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.metrics_token) >= 32
    error_message = "Use um token com pelo menos 32 caracteres."
  }
}

variable "enable_chaos" {
  description = "Valor inicial de ENABLE_CHAOS (rotas /api/v1/chaos/*). Só vale na criação da VM; depois, alterne no .env da VM."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags aplicadas a todos os recursos."
  type        = map(string)
  default = {
    projeto    = "citizentech"
    disciplina = "secure-devops"
    ambiente   = "producao"
  }
}
