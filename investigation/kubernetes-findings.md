# Incident 002 — Kubernetes Pods Start but Service Is Inaccessible

## 1. Incident Summary

**Incident ID:** INC-002  
**Component:** MiniPay API Kubernetes Deployment and Service  
**Reported Symptom:** Pods start, but users cannot access the application.  
**Investigation Status:** Static manifest review completed. No live Kubernetes cluster deployment was performed.

## 2. Findings

The original `kubernetes/starter-deployment.yaml` contains the following configuration issues:

| Finding | Original configuration | Impact |
|---|---|---|
| Placeholder image | `YOUR_IMAGE_HERE` | The deployment cannot use this as a valid application image. |
| Readiness probe port mismatch | 8081 instead of 8080 | The readiness probe cannot reach the application on its configured container port. |
| Service selector mismatch | `minipay-backend` instead of `minipay-api` | The Service does not select the API pods. |
| Service target port mismatch | 8081 instead of 8080 | Traffic would be directed to the wrong container port. |

## 3. Root Cause Analysis

The primary service-discovery issue is the mismatch between the Service selector and the pod labels.

The Deployment creates pods labelled:

`app: minipay-api`

However, the Service selects:

`app: minipay-backend`

As a result, the Service cannot identify the API pods as its backends.

Additionally, the readiness probe and Service target port use 8081, while the container declares port 8080. This creates further connectivity and readiness problems.

## 4. Corrective Actions

The corrected manifest should:

1. Replace the placeholder image with a valid application image.
2. Set the readiness probe port to 8080.
3. Change the Service selector to `app: minipay-api`.
4. Change the Service target port to 8080.
5. Verify that the application listens on port 8080 and exposes `/health`.

## 5. Validation Plan

After deployment to a Kubernetes cluster, validate using:

```bash
kubectl get pods -n minipay
kubectl get deployments -n minipay
kubectl get services -n minipay
kubectl get endpoints minipay-api -n minipay
kubectl describe deployment minipay-api -n minipay
kubectl logs deployment/minipay-api -n minipay
kubectl rollout status deployment/minipay-api -n minipay
```

Expected result: API pods become Ready, the Service has matching endpoints, and the application health endpoint responds successfully.

## 6. Validation Limitation

This investigation is based on static inspection of the supplied starter manifest. No Kubernetes cluster was available for live deployment or connectivity testing. Runtime validation remains pending.
