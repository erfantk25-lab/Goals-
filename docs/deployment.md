# Cloud Deployment Architecture

## Infrastructure Setup
The application is deployed to Microsoft Azure using Terraform (`infra/terraform`).
The infrastructure consists of:
1. **Azure Resource Group**: Logical container for all resources.
2. **Azure Database for PostgreSQL Flexible Server**: Managed relational database hosting the `users`, `goals`, `model_versions`, `system_logs`, etc.
3. **Azure Container Registry (ACR)**: Stores the Docker images built by GitHub Actions.
4. **Azure Container Apps**: Serverless container execution environment that dynamically scales the FastAPI backend based on HTTP traffic.

## Continuous Deployment (CI/CD)
Deployment is fully automated using GitHub Actions (`.github/workflows/ci.yml`).
1. Code pushed to `main` triggers linting, testing, and Bandit security scans.
2. If successful, the Docker image is built using a Multi-Stage process to minimize footprint.
3. The image is tagged and pushed to Azure Container Registry.
4. Azure Container Apps pulls the new image and performs a rolling update without downtime.
