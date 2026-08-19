# Exemplo Kubernetes com Kustomize

Este diretório organiza o mesmo stack em base + overlay, seguindo uma estrutura mais adequada para GitOps.

## Fluxo

FastAPI → Alloy → Loki → Grafana

## Subir ambiente

```bash
./up.sh
```

## Validar

```bash
kubectl kustomize kubernetes-kustomize/overlays/local
kubectl -n observability get pods
```
