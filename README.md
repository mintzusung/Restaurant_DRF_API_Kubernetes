# Orchestrated Backend Infrastructure – Food Ordering System

This repository demonstrates a **distributed backend architecture** built with **Django REST Framework (DRF)** and orchestrated via **Kubernetes**. It focuses on solving common backend challenges: service decoupling, stateful data persistence, and secure role-based access.

## 🎯 Project Core Values

* **Production-Oriented Deployment:** Instead of a simple local setup, this project uses **Kubernetes (Minikube)** to implement production patterns like **Init Containers** (for automated migrations) and **StatefulSets** (for database reliability).
* **Granular Access Control:** Implements a complete **Role-Based Access Control (RBAC)** system and **JWT Authentication**, ensuring secure interactions between Admin, Manager, Delivery Crew, and Customers.
* **High-Fidelity Environment:** Utilizes a multi-container setup with **Nginx**, **Gunicorn**, and **MySQL**, mimicking the complexity of a real-world distributed system.

---


## 🗺️Architecture Diagram
```text
        [ User / Client ]
               |
               v (HTTP Port 80)
    +-----------------------+
    |    Nginx Service      | <--- Gateway (Reverse Proxy)
    +-----------------------+
               |
               v (gunicorn Port 8000)
    +-----------------------+
    |    Django REST API    | <--- Application Layer
    |  (Pod with initCont.) |      ├─ Init: Wait-for-DB & Migrate
    +-----------------------+      └─ Main: DRF + Gunicorn
               |
               v (MySQL Port 3306)
    +-----------------------+
    | MySQL StatefulSet+PVC | <--- Persistence Layer
    +-----------------------+

```

---


##  📂Project Structure

```text
APIsProject/
├── APIsProject/               # Django Project Core Settings
│   ├── settings.py            # Configuration (Env-variable driven)
│   └── urls.py                # Main URL routing & JWT endpoints
├── APIsapp/                   # Business Logic Layer
│   ├── models.py              # Schema: Category, Menu, Cart, Order
│   ├── serializers.py         # Data Validation & Transformation
│   ├── views.py               # ViewSets & Custom Business Actions
│   ├── permissions.py         # RBAC Logic (Admin/Manager/Delivery)
│   └── urls.py                # App-level API routing
├── k8s/                       # Infrastructure as Code (IaC)
│   ├── namespace.yaml         # Resource isolation (dev-mysql)
│   ├── nginx/                 # [Gateway Layer] Reverse Proxy & Static offloading
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml     # Nginx conf (proxy_pass logic)
│   ├── web/                   # [Application Layer] Gunicorn + DRF
│   │   ├── deployment.yaml    # Includes Init Containers (wait-for-db)
│   │   ├── service.yaml       # ClusterIP for internal discovery
│   │   ├── pvc.yaml           # Static file persistence
│   │   └── configmap.yaml     # App environment variables
│   └── mysql/                 # [Persistence Layer] Database Engine
│       ├── deployment.yaml
│       ├── service.yaml       # Stable DNS: mysql-service
│       ├── pvc.yaml           # Persistent storage for MySQL data
│       └── secrets.yaml       # Sensitive DB credentials (Base64)
├── Dockerfile                 # Multi-stage production image build
├── docker-compose.yml         # Local development orchestration
└── manage.py

```


---


## 🏗️ System Evolution & Architectural Trade-offs

This project was developed through an iterative process, simulating a real-world transition from a local prototype to a **high-fidelity orchestrated system**.

---

### Stage 1: Local Monolithic Deployment

**Initial State**
* **Architecture:** Django application and SQLite database running as a single, tightly coupled unit on a local machine.
* **Trade-offs:** Fast to develop and simple to test, but lacked **High Availability (HA)**. 
* **The Problem:** Any database migration or code change created a **Single Point of Failure (SPOF)**—if the application crashed, the entire service (and its access to data) vanished.

> **Key Insight:** Tightly coupled application and database lifecycles make failure recovery unpredictable and scaling nearly impossible.

---

### Stage 2: Containerization with Docker

**Improvements**
* **Standardization:** Packaged Django, Nginx, and the environment into containers using **Docker Compose**.
* **Fidelity:** Solved the "it works on my machine" problem by ensuring consistent runtime environments across different development setups.

**Remaining Issues**
* **Logical Monolith:** While containerized, the system was still managed as a single logical unit. 
* **Coupling:** Database initialization and application startup remained dependent on one another without a formal orchestration layer.

---

### Stage 3: Kubernetes-Orchestrated Architecture (Current)

This stage achieves a **High-Fidelity Environment** by decoupling the application into independent, orchestrated components.

**Key Architectural Enhancements**

* **Layered Deployment:** Decoupled Nginx (Gateway), Django (App), and MySQL (Data) into independent workloads with explicit **Readiness/Liveness Probes**, enabling controlled traffic gating and automated recovery.
* **Database Durability:** Transitioned from SQLite to **MySQL** using **StatefulSets** and **PVCs**, ensuring data survives Pod rescheduling—a critical step in making the App layer **Stateless**.
* **Race Condition Mitigation:** Utilized **Init Containers** to enforce a deterministic startup sequence, ensuring the database is ready and migrations are applied before the application boots.

**Networking & Infrastructure Orchestration**

To ensure system reliability, I implemented a multi-layer networking strategy that isolates the internal infrastructure from external traffic.

* **Traffic Routing (Nginx):** Single entry point (Port 80) handling reverse proxying and static asset offloading to reduce backend compute load.
* **Service Discovery:** Components communicate via stable **K8s Service DNS** (e.g., `mysql-service`) rather than volatile Pod IPs, ensuring zero-downtime internal routing.
* **Secure Local Exposure & Verification:** Exposed the internal ClusterIP-based Nginx service to `localhost:8080` via `kubectl port-forward` for local development and demos.  
  This also serves as a validation mechanism, ensuring that **Service routing**, **readiness probes**, and the Nginx reverse proxy chain are functioning correctly before traffic is accepted.
* **Application-Level Security:** Enforced Django **Host Header validation** via `ALLOWED_HOSTS`, ensuring the application only responds to explicitly trusted domains.


---

## 🛠️ Backend Implementation & Business Logic

While the infrastructure ensures stability, the backend is engineered for secure, scalable food ordering operations:

### 1. Robust Access Control (RBAC)
* **JWT Authentication:** Secure stateless session management via `rest_framework_simplejwt`.
* **Granular Permissions:** Implemented custom permission classes to enforce role-based logic:
    * **Admin/Manager:** Full CRUD over Menu & Categories; Order assignment.
    * **Delivery Crew:** Read-only access to assigned orders; Status update capability (`mark_delivered`).
    * **Customer:** Personalized Cart management and Order history.

### 2. Functional Order & Cart Pipeline
* **Dynamic Cart System:** Each user session is isolated, supporting atomic operations for adding/updating/clearing items.
* **Efficient Querying:** Menu items feature advanced filtering (`?category=`) and ordering (`?sort=price`) implemented via DRF `FilterBackend`.
* **Order Lifecycle:** Optimized endpoint (`/create_from_cart/`) to convert cart items into orders with relational integrity, ensuring price snapshots at the time of purchase.

---

## 📖 API Endpoints Overview

### Auth

| Method | Endpoint              | Description                 |
| ------ | --------------------- | --------------------------- |
| POST   | `/api/token/`         | Get access + refresh tokens |
| POST   | `/api/token/refresh/` | Refresh token               |


### Categories

| Endpoint           | Description     |
| ------------------ | --------------- |
| `/api/categories/` | CRUD categories |


### Menu

| Endpoint           | Description     |
| ------------------ | --------------- |
| `/api/menu-item/`  | CRUD menu items |
| `?category=<id>`   | Filter          |
| `?sort=price`      | Sort by price   |


### Cart

| Method | Endpoint           | Description |
| ------ | ------------------ | ----------- |
| GET    | `/api/cart/`       | List items  |
| POST   | `/api/cart/`       | Add item    |
| DELETE | `/api/cart/{id}/`  | Remove item |
| DELETE | `/api/cart/clear/` | Clear cart  |


### Orders

| Method | Endpoint                           | Description              |
| ------ | ---------------------------------- | ------------------------ |
| GET    | `/api/orders/`                     | CRUD orders              |
| POST   | `/api/orders/create_from_cart/`    | Create order             |
| DELETE | `/api/orders/{id}/`                | Delete order             |
| POST   | `/api/orders/{id}/assign_order/`   | Manager assigns          |
| PATCH  | `/api/orders/{id}/mark_delivered/` | Delivery marks delivered |


### Users

These actions require **Manager/Admin** permissions.

| Endpoint                        | Description            |
| ------------------------------- | ---------------------- |
| `/api/users/`                   | List all users         |
| `/api/users/{id}/set_manager/`  | Promote to Manager     |
| `/api/users/{id}/set_delivery/` | Add Delivery crew role |


### Permissions

Custom permissions are defined in `permissions.py`:

| Permission       | Who qualifies                 |
| ---------------- | ----------------------------- |
| `IsAdmin`        | User in "Admin" group         |
| `IsManager`      | User in "Manager" group       |
| `IsDeliveryCrew` | User in "Delivery crew" group |

---

## 🚀  Running on Kubernetes (Minikube)

### 1. Start Minikube
```bash
minikube start
```

### 2. Set Minikube Docker environment
```bash
eval $(minikube docker-env)
```

### 3. Create namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 4. Deploy MySQL
```bash
kubectl apply -f k8s/mysql/
```

### 5. Deploy Web App
```bash
kubectl apply -f k8s/web/
```

### 6. Deploy Nginx
```bash
kubectl apply -f k8s/nginx/
```

### 7. Access service
#### Expose the backend service locally via port-forward (for development/demo):
```bash
kubectl port-forward svc/nginx-service 8080:80 -n dev-mysql
```

#### Then open:
```bash
http://127.0.0.1:8080
```
---


## ✅ Testing & Validation
* **End-to-End:** All endpoints validated via Postman with JWT role-based headers.
* **Resilience:** Verified data persistence using **PVC** and **Secrets** during Pod rescheduling.
* **Environment:** Simulated production workflow using **Init Containers** for schema readiness.


---


## 🧰 Tech Stack
* **Backend**: Django (DRF), Gunicorn
* **Gateway**: Nginx (Reverse Proxy)
* **Orchestration**: Kubernetes (Minikube)
* **Storage**: MySQL, PersistentVolumeClaims
* **Security**: JWT, RBAC, K8s Secrets
