# Exemplo Kubernetes puro (manifests)

Este diretório contém a mesma arquitetura em manifests nativos do Kubernetes.

## Fluxo

FastAPI → Grafana Alloy → Loki → Grafana

## Subir ambiente

```bash
./up.sh
```

## Validar

```bash
kubectl -n observability get pods
kubectl -n observability logs deploy/api-vet
kubectl -n observability logs deploy/alloy
```

## Acesso

- Gateway HTTP: `api.local` via Gateway API + Traefik
- Grafana: NodePort `30030`
- Usuário/Senha: admin/admin
