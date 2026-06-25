output "application_url" {
  value       = module.compute.app_url
  description = "The public URL of the goal planner API"
}

output "acr_login_server" {
  value       = module.registry.acr_login_server
  description = "The container registry login server URL"
}

output "key_vault_uri" {
  value       = module.security.key_vault_uri
  description = "The URI of the Key Vault"
}
