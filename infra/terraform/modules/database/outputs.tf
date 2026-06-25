output "db_server_fqdn" {
  value = azurerm_postgresql_flexible_server.db_server.fqdn
}

output "db_server_name" {
  value = azurerm_postgresql_flexible_server.db_server.name
}

output "db_database_name" {
  value = azurerm_postgresql_flexible_server_database.app_db.name
}
