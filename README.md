Distributed Backend Infrastructure – System Evolution & Kubernetes Orchestration
This project demonstrates the architectural transition of a backend service from a local monolithic setup to a fully orchestrated Kubernetes (Minikube) environment. The focus is on containerization, service decoupling, and reliable data persistence.

🚀 System Evolution & Architectural Trade-offs
This project intentionally progressed through three stages to explore and solve real-world backend infrastructure challenges.

Stage 1: Local Monolithic Deployment
Initial State: Django application using SQLite as a single deployment unit.

Limitations: High deployment risk (single point of failure), tightly coupled application/database lifecycle, and limited concurrent write capabilities of SQLite.

Stage 2: Containerization with Docker
Improvements: Packaged Django, Nginx, and database into containers using Docker Compose to standardize runtime environments across development setups.

Remaining Issues: Managed as a single logical unit; lacked granular control over individual service lifecycles and restart policies.

Stage 3: Kubernetes-Orchestrated Architecture (Current)
Transition: Decoupled Django, Nginx, and MySQL into independent Kubernetes resources to achieve better fault tolerance and resource management.

Infrastructure Highlights:

Deterministic Startup: Implemented Init Containers to execute database migrations and readiness checks, ensuring the application container only starts when dependencies are ready.

Stateful Data Persistence: Utilized PersistentVolumeClaims (PVC) and StatefulSets for MySQL to decouple data storage from Pod lifecycles, ensuring data durability through restarts.

Separation of Concerns: Independent management of ConfigMaps, Secrets, and Services for Nginx, Django, and MySQL.

🏗️ Deployment Architecture
The infrastructure is designed as a distributed multi-tier system on Kubernetes.

Plaintext

[ User / Client ]
       |
       v
  [ Nginx Service ] (Reverse Proxy & Static Routing)
       |
       v
 [ Django REST API ] (Application Layer)
       ├─ initContainer: Database Migrations & Static Collection
       └─ main container: Gunicorn + DRF
       |
       v
[ MySQL StatefulSet + PVC ] (Persistence Layer)
Key Components:
Orchestration: Kubernetes (Deployments, StatefulSets, Services, ConfigMaps, Secrets).

Persistence: MySQL with PVC for reliable stateful storage.

Gateway: Nginx as a reverse proxy for request routing and static asset delivery.

📂 Project Structure (Infrastructure Focus)
Plaintext

APIsProject/
├── APIsapp/          # Core Logic: Models, ViewSets, Permissions
├── APIsProject/      # Config: Settings, JWT Setup, URL Routing
├── k8s/              # Kubernetes Manifests
│   ├── mysql/        # Persistence: StatefulSet, PVC, Service, Secrets
│   ├── web/          # Application: Deployment (with Init Containers), Service, ConfigMap
│   └── nginx/        # Routing: Deployment, Service, ConfigMap
├── Dockerfile        # Multi-stage build for optimized image size
├── docker-compose.yml# Local development environment parity
└── manage.py
🔌 API Features & Access Control
The backend implements a Food Ordering System with complex business logic and Role-Based Access Control (RBAC):

Authentication: JWT-based access and refresh token rotation (/api/token/).

Permissions: Custom permission classes in permissions.py for Admin, Manager, and Delivery Crew.

Core Workflows: * Menu Management: Category/Menu CRUD with query filtering (?category=) and sorting (?sort=price).

Cart System: User-specific cart management (Add/Update/Delete/Clear).

Order Management: Workflow involving Cart-to-Order conversion, Manager assignment, and Delivery Crew status updates.

🚦 Running on Kubernetes (Minikube)
1. Initialize Cluster
Bash

minikube start
eval $(minikube docker-env)
2. Deploy Resources
Bash

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy database layer
kubectl apply -f k8s/mysql/

# Deploy application layer (includes migrations via Init Containers)
kubectl apply -f k8s/web/

# Deploy routing layer
kubectl apply -f k8s/nginx/
3. Access Service
Bash

kubectl port-forward svc/nginx-service 8080:80 -n dev-mysql
Then open: http://127.0.0.1:8080

🧪 Testing
API Validation: All endpoints tested via Postman, validated against JWT authentication and RBAC roles.

Reliability: Deployed on Minikube simulating a production environment with PVCs ensuring data persistence across Pod failures.

🛠️ Tech Stack
Backend: Django, Django REST Framework

Infrastructure: Kubernetes, Docker, Nginx

Database: MySQL

Auth: JWT (JSON Web Token)

Testing: Postman