# Identidade usada pelo GitHub Actions para fazer deploy SEM segredo de longa duração:
# o workflow troca o token OIDC do GitHub por um token Azure (federated credential).
# Permissão mínima: só operar a VM (Run Command), escopo restrito a ela.

resource "azurerm_user_assigned_identity" "github_deploy" {
  name                = "id-${local.name}-github-deploy"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}

resource "azurerm_federated_identity_credential" "github_deploy" {
  name                = "github-${var.github_environment}"
  resource_group_name = azurerm_resource_group.this.name
  parent_id           = azurerm_user_assigned_identity.github_deploy.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:${var.github_repository}:environment:${var.github_environment}"
}

resource "azurerm_role_assignment" "github_deploy_vm" {
  scope                = azurerm_linux_virtual_machine.app.id
  role_definition_name = "Virtual Machine Contributor"
  principal_id         = azurerm_user_assigned_identity.github_deploy.principal_id
}
