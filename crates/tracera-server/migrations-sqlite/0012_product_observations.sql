-- Append-only, product-namespaced semantic evidence. No existing data rewritten.
CREATE TABLE product_observation_baselines (
 product_id TEXT NOT NULL, baseline BIGINT NOT NULL CHECK(baseline >= 0), intents TEXT NOT NULL,
 PRIMARY KEY(product_id,baseline)
);
CREATE TABLE product_observations (
 product_id TEXT NOT NULL, observation_id TEXT NOT NULL, baseline BIGINT NOT NULL,
 capability_id TEXT, payload TEXT NOT NULL,
 PRIMARY KEY(product_id,observation_id),
 FOREIGN KEY(product_id,baseline) REFERENCES product_observation_baselines(product_id,baseline)
);
CREATE INDEX product_observations_scope ON product_observations(product_id,baseline,capability_id);
CREATE TABLE product_observation_batches (
 product_id TEXT NOT NULL, baseline BIGINT NOT NULL, batch_key TEXT NOT NULL, payload TEXT NOT NULL,
 PRIMARY KEY(product_id,baseline,batch_key),
 FOREIGN KEY(product_id,baseline) REFERENCES product_observation_baselines(product_id,baseline)
);
