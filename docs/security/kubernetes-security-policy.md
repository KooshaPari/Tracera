# Kubernetes security policy

The Helm chart is a private service by default. Before rendering or applying it,
run `scripts/verify-kubernetes-security.sh` and treat any failure as a release
stop. The gate is static and secret-free, so it is suitable for CI.

Required invariants:

- The container runs as a non-root UID, disables privilege escalation, uses the
  runtime default seccomp profile, and has a read-only root filesystem.
- Credentials are supplied through an externally managed Kubernetes `Secret`
  reference. The chart must not create placeholder or concrete passwords.
- Liveness is `/health`; readiness is `/ready`. A probe must not use an
  undocumented alias because it can mark an unhealthy process ready.
- The Service defaults to `ClusterIP`; publishing the backend port requires an
  explicit, reviewed ingress or reverse-proxy boundary with TLS and
  authentication.
- `hostNetwork` remains disabled unless a dedicated threat-model review approves
  it. Persistent data is mounted only at the data volume path.

The policy does not replace admission controls (Pod Security Admission,
NetworkPolicy, image signing, or secret-manager integration). Those controls
must be enabled by the target cluster and verified in deployment evidence.
