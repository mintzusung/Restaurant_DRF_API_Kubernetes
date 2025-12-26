# Django REST API – Food Ordering System (Kubernetes + MySQL)

This project is a **production-style backend API** built with **Django REST Framework (DRF)** and deployed on **Kubernetes (Minikube)** with **MySQL**, **Gunicorn**, and **Nginx**.

It demonstrates **real-world backend architecture**, including role-based access control, JWT authentication, persistent storage, and Kubernetes-native deployment patterns.

---

## Features

### 1. Users & Authentication

* JWT authentication (`/api/token/`, `/api/token/refresh/`)
* Three roles:

  * **Admin**
  * **Manager**
  * **Delivery crew**
* Role assignment endpoints in `UserViewSet`

---

### 2. Menu Management

* Category CRUD
* Menu Item CRUD
* Optional query filters:

  * `?category=<id>`
  * `?sort=price`

---

### 3. Cart System

* Each authenticated user has their own cart
* Add, update, delete items
* Clear cart with:

```
DELETE /api/cart/clear/
```

---

### 4. Orders

* Create order from cart:

```
POST /api/orders/create_from_cart/
```

* Role-based visibility:

  * **User:** only own orders
  * **Manager/Admin:** all orders
  * **Delivery crew:** only assigned orders
* Manager actions:

  * Assign order to delivery crew
* Delivery crew actions:

  * Mark order as delivered

---

##  Deployment Architecture

- **Django + Gunicorn**: Application server
- **MySQL**: Stateful database with PVC
- **Nginx**: Reverse proxy & static file server
- **Kubernetes**:
  - Deployment
  - Service
  - ConfigMap
  - Secret
  - PersistentVolumeClaim
- **Init Containers**:
  - Run database migrations
  - Collect static files
- **Secrets Note**:
  - secrets.example.yaml is provided for GitHub. The actual secrets.yaml containing sensitive information is not uploaded.

### Architecture Diagram
```text
[ User / Client ]
       |
       v
  [ Nginx Service ]
       |
       v
 [ Django REST API ]
       ├─ initContainer: migrate & collectstatic
       └─ main container: Django + Gunicorn
       |
       v
[ MySQL StatefulSet + PVC ]

* Each component can be independently restarted, updated, or debugged

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

## API Endpoints Overview

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

##  Running on Kubernetes (Minikube)

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

## Testing

- All API endpoints tested with JWT authentication and role-based permissions.
- Deployed on Minikube with MySQL, PVCs, ConfigMaps, Secrets, and initContainers, simulating a production-like environment.

---


## Tech Stack

- **Backend**: Django, Django REST Framework
- **Authentication**: JWT, Role-Based Access Control (RBAC)
- **Database**: MySQL
- **Reverse Proxy**: Nginx
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube)
- **Testing**: Postman


---

## System Evolution

This project intentionally went through multiple architectural stages to explore real-world backend trade-offs.

---

### Stage 1: Local Monolithic Deployment

**Initial State**

- Django application served as a single deployment unit using SQLite
- Application startup, database migrations, and service runtime were tightly coupled
- Any code change required rebuilding and restarting the entire application

**Limitations Identified**

- High deployment risk: a small change could take down the entire service
- Database limitations with SQLite: single-writer constraint and limited scaling
- Unclear startup order between application and database readiness
- Difficult to reason about failure recovery and service lifecycle

This stage was suitable for rapid development, but exposed limitations when reliability and maintainability became priorities.

---

### Stage 2: Containerization with Docker

**Improvements**

- Packaged Django, Nginx, and SQLite into containers using Docker and Docker Compose
- Standardized runtime environments
- Improved reproducibility across development setups

**Remaining Issues**

- Containers were still deployed and managed as a single logical unit
- Database initialization and application startup remained tightly coupled
- SQLite limitations persisted in multi-container or production-like environments

At this stage, the system was containerized but still effectively a **monolithic deployment**.

---

### Stage 3: Kubernetes-Orchestrated Architecture

**Transition and Key Changes**

##### 1. Separation of Deployment Responsibilities
- Django API, Nginx, and MySQL are deployed as independent Kubernetes resources
- Each component has its own lifecycle and restart policy

##### 2. Init Containers for Deterministic Startup
- Database migrations and readiness checks are executed in **Init Containers**
- Application containers start only after initialization succeeds

**Benefits**:
- Eliminates race conditions during startup
- Prevents partial or inconsistent deployments
- Makes deployment behavior predictable and repeatable

##### 3. Persistent Storage with PVC
- MySQL uses **PersistentVolumeClaims (PVC)** for data storage
- Data lifecycle is decoupled from Pod lifecycle

**Benefits**:
- Pod restarts do not result in data loss
- System tolerates crashes and redeployments gracefully

- Initially continued with SQLite, later replaced with MySQL for persistent storage

