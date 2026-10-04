# WeatherWatch — Kubernetes Microservice Assignment

WeatherWatch is a Python/FastAPI microservice application that collects weather and air-quality readings from the public Open-Meteo APIs, stores them in PostgreSQL, and displays the latest stored readings and recent history in a browser dashboard.

## Architecture

```text
Browser
   |
   v
weatherwatch-api (2 replicas)
   |
   | SQL
   v
PostgreSQL (1 replica)
   |
   | persistent storage
   v
postgres-pvc (2 GiB)

weatherwatch-collector (1 replica)
   |
   | HTTPS
   v
Open-Meteo weather + air-quality APIs
   |
   | SQL
   v
PostgreSQL
```

The browser does not connect directly to PostgreSQL. The browser calls the API, and the Collector stores external readings in the database.

## Microservices

1. **API/Web Service**
   - REST API for cities, current readings and history.
   - Serves the browser dashboard.
   - Final image: `yagnithaa/weatherwatch-api:1.0.2`.
   - Runs with 2 replicas.

2. **Collector Service**
   - REST API (`/health`, `/collect`, `/cities`).
   - Background worker polls Open-Meteo every 300 seconds by default.
   - Uses a PostgreSQL advisory lock per city.
   - Checks for an existing `(city_id, observed_at)` reading before insertion.
   - Database also enforces a unique constraint on `(city_id, observed_at)`.
   - Final image: `yagnithaa/weatherwatch-collector:1.0.4`.
   - Runs with 1 replica.

3. **PostgreSQL**
   - Separate database service.
   - Uses the `postgres-pvc` PersistentVolumeClaim.
   - Runs with 1 replica.

## Technology

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Vanilla HTML/CSS/JavaScript
- Docker
- Kubernetes
- Open-Meteo public APIs

## Local development

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8080
```

API documentation:

```text
http://localhost:8080/docs
```

Collector API:

```text
http://localhost:8001/docs
```

## Kubernetes deployment

Build and publish the final images:

```bash
docker login
make build
make push
```

Deploy the final resources:

```bash
make k8s
```

The final deployment does not include an Ingress or HPA.

For the local demonstration:

```bash
kubectl port-forward -n weatherwatch service/weatherwatch-api 8000:80
```

Then open:

```text
http://localhost:8000
```

## Kubernetes object names

| Kind | Name | Notes |
|---|---|---|
| Namespace | `weatherwatch` | |
| Deployment / Service | `weatherwatch-api` | 2 replicas, ClusterIP, port 80 -> 8000 |
| Deployment / Service | `weatherwatch-collector` | 1 replica, ClusterIP, port 80 -> 8000 |
| Deployment / Service | `postgres` | 1 replica, ClusterIP, port 5432 |
| PersistentVolumeClaim | `postgres-pvc` | 2 GiB, ReadWriteOnce |
| Secret / ConfigMap | `weatherwatch-db` / `postgres-init` | |
| External access | `kubectl port-forward` | Used for local demonstration |
| Ingress | Not deployed | |
| HorizontalPodAutoscaler | Not deployed | |

## Verify the deployment

```bash
kubectl get deployments -n weatherwatch
kubectl get pods -n weatherwatch
kubectl get svc -n weatherwatch
kubectl get pvc postgres-pvc -n weatherwatch
kubectl get ingress,hpa -n weatherwatch
kubectl logs -n weatherwatch deployment/weatherwatch-collector
```

The final cluster was verified with PostgreSQL 1/1 ready, API 2/2 ready, Collector 1/1 ready, and the PVC Bound at 2 GiB.

## Security notes

This educational project demonstrates:

- Database credentials stored in a Kubernetes Secret.
- PostgreSQL and the application Services exposed as ClusterIP.
- Pydantic request validation.
- Non-root application containers.
- Kubernetes readiness and liveness probes.
- Persistent PostgreSQL storage.

For production, add TLS, stronger secret management, authentication/authorization, NetworkPolicies, rate limiting, image scanning/signing, monitoring, backups and a managed PostgreSQL option.

## Scaling notes

The API and Collector are separate Deployments and can be scaled independently. The final assignment cluster intentionally runs 2 API replicas and 1 Collector replica. PostgreSQL remains a single persistent instance for the prototype.

## Useful commands

```bash
kubectl get pods -n weatherwatch
kubectl logs -n weatherwatch deployment/weatherwatch-collector
kubectl logs -n weatherwatch deployment/weatherwatch-api
kubectl get pvc -n weatherwatch
```
