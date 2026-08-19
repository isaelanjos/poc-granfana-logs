# Fluxo prático: Grafana Alloy, Loki e Grafana

Este documento mostra, de forma prática, como o Grafana Alloy coleta logs de containers Docker, envia os eventos para o Loki e permite que o Grafana os consulte.

## Visão do fluxo

```text
Container da API
       │
       │ stdout / stderr
       ▼
Docker Engine
       │
       │ Docker Socket
       ▼
Grafana Alloy
       │
       │ HTTP push
       ▼
Loki
       │
       │ LogQL
       ▼
Grafana
```

No projeto, o fluxo é executado pelo exemplo Docker local em:

```text
docker/docker-compose.yml
```

Os composes legados foram preservados em `documentations/legacy/docker-compose/` como referência histórica.

## 1. Subir o ambiente

Execute:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Esse comando inicia:

```text
api       → aplicação que gera os logs
alloy     → coletor de logs
loki      → backend que recebe e armazena os logs
grafana   → interface de consulta e visualização
```

O Grafana fica disponível em:

```text
http://localhost:3000
```

O dashboard de logs e o datasource Loki são provisionados automaticamente.

## 2. Como o Alloy encontra os logs

O Alloy recebe acesso ao Docker Socket através do volume definido no Compose:

```yaml
- /var/run/docker.sock:/var/run/docker.sock:ro
```

Na configuração [`../config-files/alloy/config.alloy`](../config-files/alloy/config.alloy), o componente `discovery.docker` consulta o Docker Engine:

```alloy
discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}
```

Isso permite que o Alloy descubra os containers em execução sem precisar informar manualmente o ID de cada container.

## 3. Como o Alloy seleciona a API

O projeto possui vários containers, mas o Alloy deve coletar apenas a API do modelo Alloy.

O componente `discovery.relabel` mantém o container:

```text
api-vet-alloy
```

Fluxo dessa etapa:

```text
Todos os containers Docker
          ↓
Filtro pelo nome api-vet-alloy
          ↓
Somente os logs da API
```

O mesmo componente cria o label `container` a partir do nome descoberto.

## 4. Como o Alloy coleta e processa

O componente `loki.source.docker` lê os logs do container selecionado:

```alloy
loki.source.docker "api" {
  host       = "unix:///var/run/docker.sock"
  targets    = discovery.relabel.api.output
  forward_to = [loki.process.api.receiver]
}
```

Depois, o `loki.process` remove o envelope gerado pelo Docker:

```alloy
loki.process "api" {
  stage.docker {}
  forward_to = [loki.write.local.receiver]
}
```

O pipeline prático é:

```text
discovery.docker
        ↓
discovery.relabel
        ↓
loki.source.docker
        ↓
loki.process
        ↓
loki.write
```

## 5. Como o Alloy envia para o Loki

O componente `loki.write` define o destino:

```alloy
loki.write "local" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

Dentro da rede Docker, `loki` é o nome do serviço. Por isso o Alloy não usa `localhost` para acessar o Loki.

O fluxo de envio é:

```text
Alloy
  │
  │ POST /loki/api/v1/push
  ▼
Loki:3100
```

## 6. Como o Loki recebe os logs

O Loki recebe os eventos do Alloy e os torna disponíveis para consulta.

Para verificar se o Loki está respondendo:

```bash
curl http://localhost:3100/ready
```

Para consultar os labels disponíveis:

```bash
curl http://localhost:3100/loki/api/v1/labels
```

O Loki usa armazenamento local em um volume Docker definido no Compose:

```yaml
- loki-alloy-data:/loki
```

## 7. Como o Grafana consulta o Loki

O datasource é provisionado em:

```text
config-files/grafana/provisioning/datasources/datasource.yml
```

Ele aponta para o serviço Loki dentro da rede Docker:

```yaml
url: http://loki:3100
```

O Grafana então consulta o Loki usando LogQL.

No Grafana:

```text
Explore → Loki
```

Consulta básica:

```logql
{service="api-vet"}
```

O dashboard padrão também usa essa fonte de dados e é carregado automaticamente ao iniciar o Grafana.

## 8. Teste prático completo

Com o ambiente em execução, gere um log na API:

```bash
curl http://localhost:8000/health
```

Gere também um evento de erro:

```bash
curl http://localhost:8000/pets/999
```

Depois, no Grafana, abra o dashboard `API Vet - Loki Logs` ou use no Explore:

```logql
{service="api-vet"}
```

O caminho completo será:

```text
curl
  ↓
FastAPI
  ↓
stdout do container
  ↓
Docker Socket
  ↓
Grafana Alloy
  ↓
Loki
  ↓
Grafana / LogQL
```

## 9. Parar o ambiente

```bash
docker compose -f docker/docker-compose.yml down
```

Para remover também os dados persistidos do Alloy, Loki e Grafana:

```bash
docker compose -f docker/docker-compose.yml down -v
```

