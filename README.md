# Django REST API – Food Ordering System (Kubernetes)

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
      [User]
         |
         v
   [Nginx Service]
         |
         v
   [Web Deployment]
     ├─ initContainer: migrate & collectstatic
     └─ main container: Django + Gunicorn
         |
         v
  [MySQL StatefulSet + PVC]
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

- Python 3.9
- Django 4.2
- Django REST Framework
- SimpleJWT
- MySQL
- Gunicorn
- Nginx
- Docker
- Kubernetes (Minikube)


