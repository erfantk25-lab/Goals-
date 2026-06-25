#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# ==========================================
# CONFIGURATION VARIABLES
# ==========================================
RESOURCE_GROUP="rg-goalplanner-prod"
LOCATION="eastus"
ACR_NAME="acrgoalplanner$(date +%s)"
POSTGRES_SERVER="pg-goalplanner-$(date +%s)"
POSTGRES_USER="pgadmin"
POSTGRES_PASSWORD="SuperSecurePassword123!" # In production, use Azure KeyVault!
DATABASE_NAME="goal_planner"
CONTAINER_APP_ENV="cae-goalplanner-prod"
CONTAINER_APP_NAME="ca-goalplanner-api"
IMAGE_TAG="v1.0.0"

echo "🚀 Starting Deployment of AI Goal Planner System to Azure..."

# 1. Create Resource Group
echo "📦 Creating Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Azure Container Registry (ACR)
echo "🐳 Creating Azure Container Registry: $ACR_NAME"
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

# 3. Build and Push Docker Image
echo "🔨 Building and pushing Docker image to ACR..."
az acr build --registry $ACR_NAME --image $CONTAINER_APP_NAME:$IMAGE_TAG .

# 4. Create Azure Database for PostgreSQL - Flexible Server
echo "🗄️ Creating Managed PostgreSQL Flexible Server..."
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --location $LOCATION \
  --admin-user $POSTGRES_USER \
  --admin-password $POSTGRES_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 # Caution: Restrict this IP in real prod!

echo "🗄️ Creating Database..."
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER \
  --database-name $DATABASE_NAME

# 5. Create Azure Container Apps Environment
echo "☁️ Creating Azure Container Apps Environment..."
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# 6. Deploy the Container App
echo "🚀 Deploying FastAPI App to Azure Container Apps..."
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $ACR_LOGIN_SERVER/$CONTAINER_APP_NAME:$IMAGE_TAG \
  --target-port 8000 \
  --ingress 'external' \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --env-vars \
      POSTGRES_SERVER=$POSTGRES_SERVER.postgres.database.azure.com \
      POSTGRES_USER=$POSTGRES_USER \
      POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
      POSTGRES_DB=$DATABASE_NAME \
      POSTGRES_PORT=5432 \
      OPENAI_API_KEY="" # Provide your LLM key here

# 7. Output Final URL
APP_URL=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "✅ Deployment Successful!"
echo "🌐 API is running at: https://$APP_URL"
echo "🩺 Check health: https://$APP_URL/health"
