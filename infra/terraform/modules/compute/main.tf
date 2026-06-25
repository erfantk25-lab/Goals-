resource "azurerm_log_analytics_workspace" "law" {
  name                = "${var.project_name}-${var.environment}-law"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_container_app_environment" "cae" {
  name                           = "${var.project_name}-${var.environment}-cae"
  location                       = var.location
  resource_group_name            = var.resource_group_name
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.law.id
  infrastructure_subnet_id       = var.app_subnet_id
  internal_load_balancer_enabled = false
  tags                           = var.tags
}

resource "azurerm_container_app" "app" {
  name                         = "${var.project_name}-${var.environment}-api"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [var.app_identity_id]
  }

  registry {
    server   = var.acr_login_server
    identity = var.app_identity_id
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    container {
      name   = "api"
      image  = "${var.acr_login_server}/${var.image_name}:${var.image_tag}"
      cpu    = 1.0
      memory = "2.0Gi"

      env {
        name  = "POSTGRES_SERVER"
        value = var.db_server_fqdn
      }
      env {
        name  = "POSTGRES_USER"
        value = var.db_admin_username
      }
      env {
        name  = "POSTGRES_DB"
        value = var.db_name
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "db-password"
      }
      env {
        name        = "OPENAI_API_KEY"
        secret_name = "openai-api-key"
      }
    }
    min_replicas = 1
    max_replicas = 3
  }

  secret {
    name                = "db-password"
    key_vault_secret_id = "${var.key_vault_uri}secrets/postgres-admin-password"
    identity            = var.app_identity_id
  }

  secret {
    name                = "openai-api-key"
    key_vault_secret_id = "${var.key_vault_uri}secrets/openai-api-key"
    identity            = var.app_identity_id
  }
}
