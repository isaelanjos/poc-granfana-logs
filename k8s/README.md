# POC Kubernetes de logs com Grafana Alloy + Loki + Grafana

Este diretório contém a implantação local em Kubernetes da POC original de logs do FastAPI, usando 
Gateway API para roteamento, Grafana Alloy para coleta, Loki para armazenamento e Grafana para visualização.

## Arquitetura

```text
API FastAPI (Deployment)
        │
        │ stdout JSON
        ▼
Grafana Alloy (collect + forward)
        │
        ▼
Loki (storage, query)
        │
        ▼
Grafana (dashboards)
```

O tráfego externo para a API é roteado via Gateway API + HTTPRoute. O endpoint do Gateway fica disponível com o Host `api.local`.

## Pré-requisitos

- Cluster Kubernetes local já em execução (ex.: K3s/K3d/Kind)
- `kubectl` configurado para o cluster ativo
- `docker` instalado para construir a imagem da API localmente
- `curl` e `k6` para geração de carga

## 1) Preparar a imagem da API

Na raiz do projeto:

```bash
docker build -t api-vet:latest .
```

Se o cluster estiver rodando em containerd/K3s, importe a imagem para o runtime do cluster:

```bash
sudo k3s ctr images import - < <(docker save api-vet:latest)
```

Se o cluster for um Kind ou outro runtime, adapte o comando de importação conforme o mecanismo do runtime.

## 2) Ativar suporte ao Gateway API no Traefik

O cluster local já possui o Traefik instalado, mas o provedor do Gateway API deve estar habilitado. No cluster, aplique:

```bash
kubectl patch deployment traefik -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--providers.kubernetesgateway"},{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--providers.kubernetesgateway.statusaddress.service.namespace=kube-system"},{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--providers.kubernetesgateway.statusaddress.service.name=traefik"}]'
```

Também é necessário permitir acesso às APIs do Gateway API para o serviço do Traefik:

```bash
kubectl patch clusterrole traefik-kube-system --type='json' \
  -p='[{"op":"add","path":"/rules/-","value":{"apiGroups":["gateway.networking.k8s.io"],"resources":["gatewayclasses","gateways","httproutes","referencegrants","grpcroutes","tlsroutes"],"verbs":["get","list","watch"]}},{"op":"add","path":"/rules/-","value":{"apiGroups":["gateway.networking.k8s.io"],"resources":["gatewayclasses/status","gateways/status","httproutes/status"],"verbs":["update"]}}]'
```

Essas configurações são necessárias para que o `Gateway` e o `HTTPRoute` funcionem com o controlador do Traefik.

## 3) Implantar os componentes com Kustomize

A estrutura foi reorganizada em base + overlay para facilitar GitOps e futuras variações por ambiente.

```bash
kubectl apply -k k8s/overlays/local
# ou, para a base compartilhada:
# kubectl apply -k k8s
```

Se preferir validar o manifesto gerado antes de aplicar:

```bash
kubectl kustomize k8s/overlays/local
```

## 4) Validar a API via Gateway API

A rota do Gateway foi configurada para `api.local` e a porta HTTP do Gateway exposta pelo Traefik do cluster. 
Para testar com o host correto, use `curl` com `Host` header e o IP do nó do cluster:

```bash
curl -H 'Host: api.local' http://127.0.0.1:8081/health
curl -H 'Host: api.local' http://127.0.0.1:8081/pets
```

Se o `Gateway` e o `HTTPRoute` estiverem funcionando, as requisições devem responder com sucesso. Para isso, o comando abaixo pode ser usado em um terminal separado:

```bash
kubectl -n kube-system port-forward deploy/traefik 8081:80
```

## 5) Gerar carga com k6

```bash
kubectl apply -k k8s/overlays/local
kubectl -n observability logs job/api-load-test -f
```

A carga executa em um Job do k6 e gera pedidos para a API via HTTP, com `Host: api.local`.

## 6) Validação de persistência no Loki

Acesse o Loki via `kubectl port-forward`:

```bash
kubectl -n observability port-forward svc/loki 3100:3100
```

Depois execute:

```bash
curl http://localhost:3100/ready
curl 'http://localhost:3100/loki/api/v1/labels'
curl 'http://localhost:3100/loki/api/v1/query_range?query={namespace="observability"}&limit=20&start=-1h'
```

## 7) Acessar o Grafana

O Grafana foi exposto em `NodePort` na porta `30030`:

```bash
http://192.168.100.30:30030
```

Credenciais padrão:

- Usuário: `admin`
- Senha: `admin`

O datasource `Loki` está provisionado automaticamente e o dashboard `API Vet - Loki Logs` também.

## 8) Verificar logs vindos da API

```bash
kubectl -n observability logs deploy/api-vet
kubectl -n observability logs deploy/alloy
kubectl -n observability logs deploy/grafana
```

Se a coleta estiver funcionando, o Alloy deverá listar os logs dos pods `api-vet` e encaminhar para o Loki.

## 9) Limpeza

```bash
kubectl delete -k k8s/overlays/local
# ou
# kubectl delete -k k8s
```
