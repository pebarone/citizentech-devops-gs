output "mvp_url" {
  description = "URL pública do MVP."
  value       = "https://${azurerm_public_ip.app.fqdn}"
}

output "public_ip" {
  value = azurerm_public_ip.app.ip_address
}

output "resource_group" {
  value = azurerm_resource_group.this.name
}

output "vm_name" {
  value = azurerm_linux_virtual_machine.app.name
}

# Valores para cadastrar como secrets/variables do environment "production" no GitHub.
# Não são senhas: o login OIDC só funciona a partir do repositório/environment autorizados.
output "github_actions_settings" {
  value = {
    AZURE_CLIENT_ID       = azurerm_user_assigned_identity.github_deploy.client_id
    AZURE_TENANT_ID       = azurerm_user_assigned_identity.github_deploy.tenant_id
    AZURE_SUBSCRIPTION_ID = var.subscription_id
    AZURE_RESOURCE_GROUP  = azurerm_resource_group.this.name
    AZURE_VM_NAME         = azurerm_linux_virtual_machine.app.name
    MVP_URL               = "https://${azurerm_public_ip.app.fqdn}"
  }
}
