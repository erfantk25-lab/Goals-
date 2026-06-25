output "key_vault_id" {
  value = azurerm_key_vault.kv.id
}

output "key_vault_uri" {
  value = azurerm_key_vault.kv.vault_uri
}

output "app_identity_id" {
  value = azurerm_user_assigned_identity.app_identity.id
}

output "app_identity_client_id" {
  value = azurerm_user_assigned_identity.app_identity.client_id
}

output "app_identity_principal_id" {
  value = azurerm_user_assigned_identity.app_identity.principal_id
}
