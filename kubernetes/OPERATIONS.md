# MiniPay Kubernetes Operations Guide

## 1. Apply Kubernetes Manifests

```bash
kubectl apply -f kubernetes/api.yaml
kubectl apply -f kubernetes/database.yaml
```

## 2. Check Deployment Status

```bash
kubectl get namespaces
kubectl get pods -n minipay
kubectl get deployments -n minipay
kubectl get services -n minipay
kubectl get pvc -n minipay
```

## 3. Check Service Endpoints

```bash
kubectl get endpoints minipay-api -n minipay
kubectl get endpoints minipay-db -n minipay
```

The API Service should have endpoints corresponding to ready API pods.

## 4. Inspect Application Logs

```bash
kubectl logs deployment/minipay-api -n minipay
kubectl logs deployment/minipay-db -n minipay
```

For a specific pod:

```bash
kubectl logs POD_NAME -n minipay
```

## 5. Troubleshoot Pods

```bash
kubectl describe pods -n minipay
kubectl describe deployment minipay-api -n minipay
kubectl get events -n minipay --sort-by=.metadata.creationTimestamp
```

Check readiness and liveness probe failures, image-pull errors, resource constraints, and database connectivity.

## 6. Restart and Roll Back

```bash
kubectl rollout restart deployment/minipay-api -n minipay
kubectl rollout status deployment/minipay-api -n minipay
kubectl rollout history deployment/minipay-api -n minipay
kubectl rollout undo deployment/minipay-api -n minipay
```

## 7. Access the API Locally

```bash
kubectl port-forward service/minipay-api 8080:80 -n minipay
```

Then access:

`http://localhost:8080/health`

## 8. Deployment Prerequisites

- A Kubernetes cluster and configured `kubectl` context.
- A valid MiniPay API container image available to the cluster.
- A suitable StorageClass for the PostgreSQL PVC.
- Database and API secrets created with secure values.
- PostgreSQL initialized and accessible before API readiness is expected.

## 9. Execution Status

These commands are documented for operational use. They have not been executed against a live Kubernetes cluster as part of this assessment.
