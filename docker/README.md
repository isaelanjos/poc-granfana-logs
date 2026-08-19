# Exemplo Docker

Este diretório executa a mesma arquitetura local em containers Docker Compose.

## Fluxo

FastAPI → stdout → Docker → Grafana Alloy → Loki → Grafana

## Subir ambiente

```bash
./up.sh
```

## Validação rápida

```bash
curl http://localhost:8000/health
curl http://localhost:8000/pets
curl http://localhost:3100/ready
```

## Acesso

- API: http://localhost:8000
- Grafana: http://localhost:3000
- Usuário/Senha: admin/admin

## Parar ambiente

```bash
docker compose down
```
