import * as k8s from "@pulumi/kubernetes";

// Wrap all existing Kubernetes manifests under k8s/ using a single ConfigGroup.
// This keeps behavior identical to kubectl/apply of the YAML files, but moves
// orchestration into code (Pulumi Node.js runtime).

const k8sFiles = [
  "../k8s/namespace.yaml",
  "../k8s/postgres-deployment.yaml",
  "../k8s/redis-deployment.yaml",
  "../k8s/nats-deployment.yaml",
  "../k8s/backend-deployment.yaml",
  "../k8s/api-deployment.yaml",
  "../k8s/configmap.yaml",
  "../k8s/secret.yaml",
  "../k8s/ingress.yaml",
  "../k8s/hpa.yaml",
  "../k8s/networkpolicy.yaml",
  "../k8s/monitoring.yaml",
];

export const tracertmK8s = new k8s.yaml.ConfigGroup("tracertm-k8s", {
  files: k8sFiles,
});

