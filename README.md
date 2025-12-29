# Orchestrated Backend Infrastructure – Food Ordering System

This repository demonstrates a **distributed backend architecture** built with **Django REST Framework (DRF)** and orchestrated via **Kubernetes**. It focuses on solving common backend challenges: service decoupling, stateful data persistence, and secure role-based access.

### 🌟 Project Core Values

* **Production-Oriented Deployment:** Instead of a simple local setup, this project uses **Kubernetes (Minikube)** to implement production patterns like **Init Containers** (for automated migrations) and **StatefulSets** (for database reliability).
* **Granular Access Control:** Implements a complete **Role-Based Access Control (RBAC)** system and **JWT Authentication**, ensuring secure interactions between Admin, Manager, Delivery Crew, and Customers.
* **High-Fidelity Environment:** Utilizes a multi-container setup with **Nginx**, **Gunicorn**, and **MySQL**, mimicking the complexity of a real-world distributed system.

---

## 🚀 System Evolution & Architectural Trade-offs

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


**Separation of Deployment Responsibilities**
* Decoupled the monolithic logic into distinct layers (Nginx, Django, MySQL), managed as independent Kubernetes workloads.
* Each component now has its own **Lifecycle and Restart Policy**, improving system resilience.

**Deterministic Startup with Init Containers**
* **Problem:** Distributed systems often face "race conditions" where the app starts before the database is ready.
* **Solution:** Implemented **Init Containers** to handle database migrations and connectivity checks.
* **Value:** Ensures the main Django container only starts when the infrastructure is ready, making deployments predictable.

**Database Strategy: Migration from SQLite to MySQL**
* **Technical Challenge:** Identified that SQLite’s file-based storage is incompatible with the **ephemeral nature** of Kubernetes Pods. In a containerized environment, local file changes are lost upon Pod termination or rescheduling.
* **Architectural Decision:** Migrated the persistence layer to **MySQL** utilizing **StatefulSets** and **PersistentVolumeClaims (PVC)** to decouple data storage from the compute lifecycle.
* **Impact:** Achieved guaranteed **Data Durability** and system resilience. The application layer became truly **Stateless**, satisfying a core requirement for scalable distributed systems.

**Networking & Infrastructure Orchestration**
To ensure system reliability and security, I implemented a multi-layer networking strategy that decouples the application from the underlying infrastructure.

#### 🌐 Traffic Routing Logic:
* **Gateway Layer (Nginx):** Acts as the single entry point, listening on port `80`. It performs reverse proxying to the application layer and handles static asset offloading to reduce backend load.
* **Application Layer (Django):** Operates on port `8000`. It is entirely **environment-agnostic**, retrieving its database location via the `DB_HOST` environment variable injected by Kubernetes.
* **Database Layer (MySQL):** Isolated within the internal network on port `3306`, accessible only through the stable DNS handle `mysql-service`.

#### 🧬 Service Discovery & Dependency Management:
* **Stable Identifiers:** By utilizing **Kubernetes Services (ClusterIP)**, components communicate via stable DNS names (e.g., `mysql-service`) rather than volatile Pod IPs. This ensures zero-downtime internal routing during Pod rescheduling.
* **Deterministic Startup (Init Containers):** * Implemented a `wait-for-db` logic using **Init Containers** to check port 3306 availability via `netcat`.
    * This prevents "Race Conditions" where the Django app might crash if it attempts to connect before the MySQL service is fully operational.
    * Database migrations (`python manage.py migrate`) are executed within this stage to ensure schema readiness before the main application boots.

#### 🔐 Secure External Mapping:
* **Local Development:** Bridged the isolated K8s network to the host using `kubectl port-forward` on port `8080`.
* **Host Validation:** Leveraged Django's `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to perform strict **Host Header Validation**, ensuring the application only processes requests routed through the verified Nginx gateway.


---


### Architecture Diagram
```text
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
```

---


##  Project Structure

```text
APIsProject/
├── APIsapp/
│   ├── models.py         # Category, MenuItem, Cart, Order, OrderItem
│   ├── serializers.py    # DRF serializers including nested relations
│   ├── views.py          # ViewSets + custom actions
│   ├── permissions.py    # Custom role-based permissions
│   └── urls.py           # Router endpoints
│
├── APIsProject/
│   ├── settings.py       # DRF, JWT, DB, static, installed apps
│   └── urls.py           # JWT endpoints + app endpoints
├── k8s/
│   ├── namespace.yaml
│   ├── mysql/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── pvc.yaml
│   │   └── secrets.yaml
│   ├── web/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── pvc.yaml
│   │   └── configmap.yaml
│   └── nginx/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
├── Dockerfile
├── docker-compose.yml      # Local development
├── manage.py
├── Pipfile / Pipfile.lock
├── staticfiles/            # Collected static files
└── README.md
```

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

## 🛠️ API Endpoints Overview

### Auth

| Method | Endpoint              | Description                 |
| ------ | --------------------- | --------------------------- |
| POST   | `/api/token/`         | Get access + refresh tokens |
| POST   | `/api/token/refresh/` | Refresh token               |

---

### Categories

| Endpoint           | Description     |
| ------------------ | --------------- |
| `/api/categories/` | CRUD categories |

---

### Menu

| Endpoint           | Description     |
| ------------------ | --------------- |
| `/api/menu-item/`  | CRUD menu items |
| `?category=<id>`   | Filter          |
| `?sort=price`      | Sort by price   |

---

### Cart

| Method | Endpoint           | Description |
| ------ | ------------------ | ----------- |
| GET    | `/api/cart/`       | List items  |
| POST   | `/api/cart/`       | Add item    |
| DELETE | `/api/cart/{id}/`  | Remove item |
| DELETE | `/api/cart/clear/` | Clear cart  |

---

### Orders

| Method | Endpoint                           | Description              |
| ------ | ---------------------------------- | ------------------------ |
| GET    | `/api/orders/`                     | CRUD orders              |
| POST   | `/api/orders/create_from_cart/`    | Create order             |
| DELETE | `/api/orders/{id}/`                | Delete order             |
| POST   | `/api/orders/{id}/assign_order/`   | Manager assigns          |
| PATCH  | `/api/orders/{id}/mark_delivered/` | Delivery marks delivered |

---

### Users

These actions require **Manager/Admin** permissions.

| Endpoint                        | Description            |
| ------------------------------- | ---------------------- |
| `/api/users/`                   | List all users         |
| `/api/users/{id}/set_manager/`  | Promote to Manager     |
| `/api/users/{id}/set_delivery/` | Add Delivery crew role |

---

## Permissions

Custom permissions are defined in `permissions.py`:

| Permission       | Who qualifies                 |
| ---------------- | ----------------------------- |
| `IsAdmin`        | User in "Admin" group         |
| `IsManager`      | User in "Manager" group       |
| `IsDeliveryCrew` | User in "Delivery crew" group |

---

## 🛠️  Running on Kubernetes (Minikube)

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
```bash
kubectl port-forward svc/nginx-service 8080:80 -n dev-mysql
```
#### Then open:
```bash
http://127.0.0.1:8080
```
---

## Database

- **MySQL** (Kubernetes Stateful setup)
- Credentials stored in **Kubernetes Secrets**
- Data persisted via **PersistentVolumeClaim**

---

## 🛠️ Testing

- All API endpoints tested with JWT authentication and role-based permissions.
- Deployed on Minikube with MySQL, PVCs, ConfigMaps, Secrets, and initContainers, simulating a production-like environment.

---


## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Authentication**: JWT, Role-Based Access Control (RBAC)
- **Database**: MySQL
- **Reverse Proxy**: Nginx
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube)
- **Testing**: Postman
