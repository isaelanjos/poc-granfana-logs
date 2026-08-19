# POC: observabilidade local com API, Alloy, Loki e Grafana

Este repositório reúne a mesma arquitetura de observabilidade implementada de 4 formas diferentes para execução local:

- Docker Compose
- Kubernetes puro com manifests
- Kubernetes com Kustomize
- Kubernetes com Helm

## Visão geral da arquitetura

```text
API FastAPI -> stdout -> Coletor -> Loki -> Grafana
```

Nos exemplos locais, a coleta é feita com Grafana Alloy, o armazenamento com Loki e a visualização com Grafana.

## Estrutura do repositório

- [docker/](docker/) — exemplo em Docker Compose
- [kubernetes-manifests/](kubernetes-manifests/) — exemplo em Kubernetes puro
- [kubernetes-kustomize/](kubernetes-kustomize/) — exemplo em Kustomize
- [kubernetes-helm/](kubernetes-helm/) — exemplo em Helm
- [config-files/](config-files/) — arquivos de configuração dos serviços (Alloy, Grafana, Loki, Promtail, Fluent Bit)
- [documentations/](documentations/) — documentação, diagramas e materiais de apoio
- [k8s/](k8s/) — material de referência/compatibilidade do stack em Kubernetes

## Subir um exemplo

Escolha o caminho desejado:

```bash
./up-docker.sh
./up-kubernetes-manifests.sh
./up-kubernetes-kustomize.sh
./up-kubernetes-helm.sh
```

## Documentação por exemplo

- Para mais detalhes de como funciona no Docker, clique em [docker/README.md](docker/README.md).
- Para mais detalhes de como funciona no Kubernetes puro, clique em [kubernetes-manifests/README.md](kubernetes-manifests/README.md).
- Para mais detalhes de como funciona no Kubernetes com Kustomize, clique em [kubernetes-kustomize/README.md](kubernetes-kustomize/README.md).
- Para mais detalhes de como funciona no Kubernetes com Helm, clique em [kubernetes-helm/README.md](kubernetes-helm/README.md).
- Para diagramas, fluxos e materiais de apoio, consulte [documentations/README.md](documentations/README.md).

## Acesso local

- API: http://localhost:8000 para Docker; via Gateway/NodePort para Kubernetes
- Grafana: http://localhost:3000 no Docker; http://<node-ip>:30030 no cluster
- Credenciais padrão: admin / admin

## Validação

Após subir qualquer exemplo, valide:

```bash
curl http://localhost:8000/health
kubectl -n observability get pods
kubectl -n observability logs deploy/api-vet
```
