# EduGraphAI - Kubernetes Deployment Guide

This directory contains the production-style Kubernetes manifests for **EduGraphAI**, designed for academic evaluation, final-year project demonstration, and viva presentation.

---

## 1. Architecture Summary

| Component | Resource Type | Target Port | NodePort | Purpose |
|---|---|---|---|---|
| **Namespace** | `Namespace` | - | - | Logical isolation (`edugraphai`) |
| **ConfigMap** | `ConfigMap` | - | - | Application configuration (`edugraph-config`) |
| **Secret** | `Secret` | - | - | Secure credentials (`edugraph-secret`) |
| **SQLite DB** | `PersistentVolumeClaim` | - | - | User auth persistence (`backend-data-pvc`) |
| **Backend** | `Deployment` + `Service` | `8000` | `30800` | FastAPI RAG backend with probes |
| **Frontend** | `Deployment` + `Service` | `3000` | `30080` | Next.js standalone UI with probes |
| **Neo4j** *(Optional)* | `StatefulSet` + `Service` | `7474`, `7687` | - | In-cluster graph database with PVC |
| **Ollama** | *External / Host-Managed* | `11434` | - | Hardware-accelerated local LLM inference |

---

## 2. Quick Start: Deploy Locally

### Step 1: Start your Local Kubernetes Cluster
Enable Kubernetes in **Docker Desktop** (Settings > Kubernetes > Enable Kubernetes), or start Minikube:
```bash
minikube start
```

### Step 2: Build or Load Container Images
If using Minikube or Kind, point your terminal to the cluster's Docker daemon or load images:
```bash
# Minikube:
eval $(minikube docker-env)
docker build -t edugraph-backend:latest ./Backend
docker build -t edugraph-frontend:latest ./frontend

# Or standard Docker Desktop Kubernetes:
docker build -t edugraph-backend:latest ./Backend
docker build -t edugraph-frontend:latest ./frontend
```

### Step 3: Create the Namespace and Secrets
Never commit secrets to Git. Create the Kubernetes Secret directly via the CLI:
```bash
# 1. Create the namespace
kubectl apply -f k8s/00-namespace.yaml

# 2. Create the secret securely (add LLM_API_KEY if using hosted cloud LLM)
kubectl create secret generic edugraph-secret \
  --namespace=edugraphai \
  --from-literal=NEO4J_PASSWORD="YourStrongPassword123!" \
  --from-literal=JWT_SECRET_KEY="c8f1e2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1" \
  --from-literal=LLM_API_KEY="your-optional-api-key"
```

### Step 4: Deploy the Workloads
Apply the manifests using Kustomize:
```bash
kubectl apply -k k8s/
```
*(For production domain routing and automated HTTPS TLS termination, see `k8s/09-ingress.example.yaml`)*

*Or apply individually in sequence:*
```bash
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/03-pvc.yaml
kubectl apply -f k8s/04-backend-deployment.yaml
kubectl apply -f k8s/05-backend-service.yaml
kubectl apply -f k8s/06-frontend-deployment.yaml
kubectl apply -f k8s/07-frontend-service.yaml
```

*(Optional) If you want Neo4j running inside Kubernetes instead of on your host:*
```bash
kubectl apply -f k8s/08-neo4j-statefulset.yaml
```

---

## 3. Verify Deployment

Check that all pods, services, and volume claims are running and healthy:
```bash
# View pod status
kubectl get pods -n edugraphai

# View services and NodePorts
kubectl get svc -n edugraphai

# View PVC status
kubectl get pvc -n edugraphai

# View container logs
kubectl logs -f -l app=edugraph-backend -n edugraphai
kubectl logs -f -l app=edugraph-frontend -n edugraphai
```

---

## 4. Access the Application

- **Frontend Application**: `http://localhost:30080` (or `http://<minikube-ip>:30080`)
- **Backend API Docs**: `http://localhost:30800/docs`

*For Minikube users who cannot access NodePorts directly on localhost:*
```bash
minikube service edugraph-frontend -n edugraphai
```

---

## 5. Stop and Clean Up

To delete all deployed resources:
```bash
kubectl delete -k k8s/
kubectl delete secret edugraph-secret -n edugraphai
kubectl delete namespace edugraphai
```
