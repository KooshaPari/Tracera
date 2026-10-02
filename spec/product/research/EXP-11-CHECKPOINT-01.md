# EXP-11 executed checkpoint — dependency-footprint soundness

Date: 2026-09-30. Scope: synthetic reference model, not Tracera Rust proof.

Result: 6/6 semantic checks passed; 4/4 omitted-dependency mutation controls detected.

Promoted invariant: inferred or missing absence cannot establish independence. Inference may conservatively expand a footprint and cause extra rechecks. Shrinking a footprint requires deterministic/accepted evidence of irrelevance or an explicit compatibility proof.

Cases covered dependency-lock change, unrelated source change, missing runtime dependency, stale index revision, generated-client/schema chain, and conservative inferred-positive invalidation.

Source SHA-256: 79ae34313a554fbad7fb7ab81055b203e19d4a6c0f4c4cf1cc0c84b3b4d4ebc1.
Result SHA-256: 381f482ed8a9df47a04e8c3d065d003f9d23964b3abfb17926aec769577fb0ea.

Limits: synthetic dependency truth; no Tracera Rust execution; no real compiler/index/runtime extraction; no precision/recall benchmark; no certificate-revocation fanout yet.

Next: typed suspect/invalidation propagation and the real current-Rust assessment witness.
