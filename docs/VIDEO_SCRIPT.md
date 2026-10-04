# Video re-recording script (about 5 minutes, WITH narration)

Record against the final project and final cluster so every name, image tag and replica count matches the report.

Names that should appear on screen:
`weatherwatch`, `weatherwatch-api`, `weatherwatch-collector`, `postgres`, `postgres-pvc`.

| # | Say (approx.) | Show / run |
|---|---|---|
| 1 | "This is WeatherWatch: an API/web service, a collector service and PostgreSQL running on Kubernetes." | Architecture diagram / README |
| 2 | "The final Docker images are published on Docker Hub and referenced by the Kubernetes Deployments." | `grep -R "image:" k8s/*-deployment.yaml` |
| 3 | "Everything is deployed in the weatherwatch namespace." | `make k8s` or the individual kubectl apply commands |
| 4 | "The final deployment has two API replicas, one Collector replica and one PostgreSQL replica." | `kubectl get deployments -n weatherwatch` |
| 5 | "All application Services are ClusterIP services. For this local demonstration I use port-forward to the API." | `kubectl get services -n weatherwatch` then `kubectl port-forward -n weatherwatch service/weatherwatch-api 8000:80` |
| 6 | "PostgreSQL uses a persistent two-gigabyte volume." | `kubectl get pvc postgres-pvc -n weatherwatch` |
| 7 | "The API health endpoint confirms that the service is running." | Open `http://localhost:8000/health` |
| 8 | "The dashboard lets me choose a configured city and view the latest stored weather and air-quality readings and recent history." | Browser dashboard; show Bengaluru, then London and Refresh |
| 9 | "The Collector periodically reads Open-Meteo. Duplicate timestamps are skipped so the same city observation is not stored twice." | `kubectl logs -n weatherwatch deployment/weatherwatch-collector` |
| 10 | "The final cluster has no deployed Ingress or HorizontalPodAutoscaler." | `kubectl get ingress,hpa -n weatherwatch` |
| 11 | "This demonstration, the report and the project files all describe the same final configuration." | GitHub repository / project folder |

After recording, add the exact video file name to report section 8.
