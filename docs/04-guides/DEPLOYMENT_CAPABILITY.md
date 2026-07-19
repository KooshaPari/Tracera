# Deployment capability probe

Run `deploy/kubernetes/capability-report.sh` to inspect local deployment tooling
without changing kubeconfig, creating namespaces, pulling images, or touching secrets.

```sh
./deploy/kubernetes/capability-report.sh
./deploy/kubernetes/capability-report.sh --json
```

It reports Helm lint, Kubernetes reachability, Docker Compose, and optional local
cluster tools. Safe chart checks remain:

```sh
helm lint deploy/kubernetes
helm template tracera-smoke deploy/kubernetes >/tmp/tracera-rendered.yaml
```
