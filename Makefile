DOCKERHUB_USER ?= yagnithaa
API_VERSION    ?= 1.0.2
COLLECTOR_VERSION ?= 1.0.4

.PHONY: build push up down k8s k8s-delete status

build:
	docker build -t $(DOCKERHUB_USER)/weatherwatch-api:$(API_VERSION) -f api_service/Dockerfile .
	docker build -t $(DOCKERHUB_USER)/weatherwatch-collector:$(COLLECTOR_VERSION) ./collector_service

push:
	docker push $(DOCKERHUB_USER)/weatherwatch-api:$(API_VERSION)
	docker push $(DOCKERHUB_USER)/weatherwatch-collector:$(COLLECTOR_VERSION)

up:
	docker compose up --build

down:
	docker compose down

k8s:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/postgres.yaml
	kubectl apply -f k8s/api-deployment.yaml
	kubectl apply -f k8s/api-service.yaml
	kubectl apply -f k8s/collector-deployment.yaml
	kubectl apply -f k8s/collector-service.yaml

k8s-delete:
	kubectl delete namespace weatherwatch

status:
	kubectl get pods,svc,pvc -n weatherwatch
