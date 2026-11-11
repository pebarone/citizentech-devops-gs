resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

locals {
  name     = "${var.project}-${random_string.suffix.result}"
  dns_name = "${var.project}-${random_string.suffix.result}"
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${local.name}"
  location = var.location
  tags     = var.tags
}

# ---- Rede ------------------------------------------------------------------------

resource "azurerm_virtual_network" "this" {
  name                = "vnet-${local.name}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space       = ["10.20.0.0/16"]
  tags                = var.tags
}

resource "azurerm_subnet" "app" {
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.20.1.0/24"]
}

resource "azurerm_network_security_group" "app" {
  name                = "nsg-${local.name}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags

  # Tráfego público do cidadão: só HTTP (redireciona) e HTTPS.
  security_rule {
    name                       = "allow-http"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow-https"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  # Porta de administração: só dos CIDRs explicitamente autorizados (nunca 0.0.0.0/0).
  dynamic "security_rule" {
    for_each = length(var.admin_cidrs) > 0 ? [1] : []
    content {
      name                       = "allow-ssh-admin"
      priority                   = 200
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "22"
      source_address_prefixes    = var.admin_cidrs
      destination_address_prefix = "*"
    }
  }

  # Nega explicitamente o resto da internet (deixa a intenção visível no portal).
  security_rule {
    name                       = "deny-all-inbound"
    priority                   = 4000
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}

resource "azurerm_public_ip" "app" {
  name                = "pip-${local.name}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = local.dns_name
  tags                = var.tags
}

resource "azurerm_network_interface" "app" {
  name                = "nic-${local.name}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags

  ip_configuration {
    name                          = "primary"
    subnet_id                     = azurerm_subnet.app.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.app.id
  }
}

# ---- VM ------------------------------------------------------------------------

resource "azurerm_linux_virtual_machine" "app" {
  name                            = "vm-${local.name}"
  location                        = azurerm_resource_group.this.location
  resource_group_name             = azurerm_resource_group.this.name
  size                            = var.vm_size
  admin_username                  = var.admin_username
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.app.id]
  tags                            = var.tags

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.admin_ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 30
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  # Instala Docker e grava o .env da stack. O conteúdo fica no state remoto (protegido), não no repo.
  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tftpl", {
    site_address  = azurerm_public_ip.app.fqdn
    metrics_token = var.metrics_token
    enable_chaos  = var.enable_chaos
  }))

  # Sem identidade gerenciada na VM: os containers não têm credencial Azure para obter via IMDS.

  boot_diagnostics {}

  lifecycle {
    # Mudar custom_data RECRIA a VM. Depois do primeiro apply, ajustes no .env são feitos
    # na própria VM (ver docs/evidencias.md), não por aqui.
    ignore_changes = [custom_data]
  }
}
