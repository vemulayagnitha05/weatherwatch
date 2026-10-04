# Kubernetes notes

The final assignment configuration uses the following resources in the `weatherwatch` namespace:

- `weatherwatch-api` Deployment: 2 replicas, image `yagnithaa/weatherwatch-api:1.0.2`
- `weatherwatch-api` Service: ClusterIP, port 80 -> 8000
- `weatherwatch-collector` Deployment: 1 replica, image `yagnithaa/weatherwatch-collector:1.0.4`
- `weatherwatch-collector` Service: ClusterIP, port 80 -> 8000
- `postgres` Deployment: 1 replica, image `postgres:16-alpine`
- `postgres` Service: ClusterIP, port 5432
- `postgres-pvc`: 2 GiB, ReadWriteOnce
- `weatherwatch-db` Secret
- `postgres-init` ConfigMap

No Ingress or HorizontalPodAutoscaler is deployed in the final cluster.

For a local browser demonstration:

```bash
kubectl port-forward -n weatherwatch service/weatherwatch-api 8000:80
```

Then open `http://localhost:8000`.

Useful checks:

```bash
kubectl get pods -n weatherwatch
kubectl get svc -n weatherwatch
kubectl get pvc -n weatherwatch
kubectl get deployments -n weatherwatch
kubectl logs -n weatherwatch deployment/weatherwatch-collector
```
