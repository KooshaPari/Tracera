SELECT d.*
FROM evidence_reuse_decisions_v1 d
JOIN product_baselines_v1 target ON target.baseline_id = d.target_baseline_id
JOIN product_observations_v1 o ON o.observation_id = d.observation_id
JOIN product_baselines_v1 source ON source.baseline_id = o.baseline_id
WHERE target.product_id = ?1
  AND o.product_id = ?1
  AND source.product_id = ?1
  AND d.target_baseline_id = ?2
  AND d.target_candidate_ref = ?3
ORDER BY d.decided_at, d.reuse_decision_id
LIMIT ?4
