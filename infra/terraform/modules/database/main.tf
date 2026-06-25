resource "azurerm_private_dns_zone" "db_dns" {
  name                = "${var.project_name}-${var.environment}.postgres.database.azure.com"
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "db_dns_link" {
  name                  = "${var.project_name}-${var.environment}-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.db_dns.name
  virtual_network_id    = var.vnet_id
  resource_group_name   = var.resource_group_name
  tags                  = var.tags
}

resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "_%@"
}

resource "azurerm_key_vault_secret" "db_password_secret" {
  name         = "postgres-admin-password"
  value        = random_password.db_password.result
  key_vault_id = var.key_vault_id
}

resource "azurerm_postgresql_flexible_server" "db_server" {
  name                   = "${var.project_name}-${var.environment}-psql"
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  delegated_subnet_id    = var.db_subnet_id
  private_dns_zone_id    = azurerm_private_dns_zone.db_dns.id
  administrator_login    = var.db_admin_username
  administrator_password = random_password.db_password.result
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  backup_retention_days  = 7
  tags                   = var.tags

  depends_on = [azurerm_private_dns_zone_virtual_network_link.db_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "app_db" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.db_server.id
  collation = "en_US.utf8"
  charset   = "utf8"
}
