# Cloud Architecture (Azure Deployment)

## Architecture Diagram

```mermaid
graph TD
    User([End User]) --> |HTTPS POST| ACA[Azure Container Apps\n(FastAPI Docker Container)]
    
    subgraph Azure Cloud Environment
        ACA --> |Inference| ML[Scikit-Learn Model\n(joblib)]
        ACA --> |TCP 5432 / SQLAlchemy| PG[Azure Database for PostgreSQL\nFlexible Server]
        ACA --> |JSON Logs| LAW[Log Analytics Workspace]
    end
    
    ACA --> |HTTPS POST| LLM[OpenAI API / Hosted LLM]

    style ACA fill:#0078D4,stroke:#fff,color:#fff
    style PG fill:#0078D4,stroke:#fff,color:#fff
    style LAW fill:#505050,stroke:#fff,color:#fff
    style ML fill:#107C10,stroke:#fff,color:#fff
```

## Why Azure? (Trade-offs & Rationale)

1. **Azure Container Apps (ACA)**: Chosen over raw Kubernetes (AKS) or Azure App Service. ACA provides a Serverless container execution environment specifically optimized for microservices. It automatically scales based on HTTP traffic (down to zero, saving costs), abstracts away Kubernetes complexity, and integrates natively with Azure Log Analytics for our JSON-formatted logs.
2. **Azure Database for PostgreSQL (Flexible Server)**: A fully managed, production-ready relational database. It handles automated backups, patching, and offers connection pooling (pgBouncer) out of the box, which is critical for scaling FastAPI applications that spin up many database connections.
3. **Stateless Design**: Our container is completely stateless. The ML model (`.joblib`) is baked into the Docker image, and all state (Goals, Predictions, LLM Plans) is stored securely in PostgreSQL.

## Deployment Strategy
We utilize a **Container-Based Strategy**. The application is built using a slim Dockerfile, pushed to Azure Container Registry (ACR), and deployed to ACA. Environment variables securely inject database credentials and LLM API keys without hardcoding secrets in the source code.
