resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
  tags     = local.tags
}

locals {
  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

module "networking" {
  source              = "../../modules/networking"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  environment         = var.environment
  project_name        = var.project_name
  vnet_address_space  = var.vnet_address_space
  app_subnet_prefix   = var.app_subnet_prefix
  db_subnet_prefix    = var.db_subnet_prefix
  tags                = local.tags
}

module "security" {
  source              = "../../modules/security"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  environment         = var.environment
  project_name        = var.project_name
  tags                = local.tags
}

module "registry" {
  source                    = "../../modules/registry"
  resource_group_name       = azurerm_resource_group.rg.name
  location                  = azurerm_resource_group.rg.location
  environment               = var.environment
  project_name              = var.project_name
  app_identity_principal_id = module.security.app_identity_principal_id
  tags                      = local.tags
}

module "database" {
  source              = "../../modules/database"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  environment         = var.environment
  project_name        = var.project_name
  vnet_id             = module.networking.vnet_id
  db_subnet_id        = module.networking.db_subnet_id
  key_vault_id        = module.security.key_vault_id
  db_admin_username   = var.db_admin_username
  db_name             = var.db_name
  tags                = local.tags
}

module "compute" {
  source              = "../../modules/compute"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  environment         = var.environment
  project_name        = var.project_name
  app_subnet_id       = module.networking.app_subnet_id
  app_identity_id     = module.security.app_identity_id
  acr_login_server    = module.registry.acr_login_server
  image_name          = var.image_name
  image_tag           = var.image_tag
  db_server_fqdn      = module.database.db_server_fqdn
  db_admin_username   = var.db_admin_username
  db_name             = var.db_name
  key_vault_uri       = module.security.key_vault_uri
  tags                = local.tags
}
