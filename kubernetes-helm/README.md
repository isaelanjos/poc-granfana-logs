# Exemplo Kubernetes com Helm

Este diretório empacota a mesma arquitetura em um Helm chart local para execução no cluster.

## Fluxo

FastAPI → Alloy → Loki → Grafana

## Subir ambiente

```bash
./up.sh
```

## Validar

```bash
helm template observability .
helm lint .
kubectl -n observability get pods
```
