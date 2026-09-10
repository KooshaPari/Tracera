//! Cloudflare R2 artifact storage client (S3-compatible, AWS Signature v4).
//! Activates when env `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
//! and `R2_BUCKET` are all set. Falls back to no-op when any is unset.
//!
//! Uses the official `aws-sdk-s3` crate pointing at Cloudflare's R2 endpoint
//! (`https://<ACCOUNT_ID>.r2.cloudflarestorage.com`).

use std::sync::Arc;
use tracing::{debug, info, warn};

#[derive(Clone)]
pub struct R2Client {
    inner: Arc<R2Inner>,
}

enum R2Inner {
    Disabled,
    Enabled {
        client: aws_sdk_s3::Client,
        bucket: String,
    },
}

impl R2Client {
    pub fn from_env() -> Self {
        let account = std::env::var("R2_ACCOUNT_ID").ok();
        let access = std::env::var("R2_ACCESS_KEY_ID").ok();
        let secret = std::env::var("R2_SECRET_ACCESS_KEY").ok();
        let bucket = std::env::var("R2_BUCKET").ok();

        if account.is_none() || access.is_none() || secret.is_none() || bucket.is_none() {
            debug!("R2 env vars incomplete; artifact storage disabled (no-op)");
            return Self { inner: Arc::new(R2Inner::Disabled) };
        }

        let account = account.unwrap();
        let access = access.unwrap();
        let secret = secret.unwrap();
        let bucket = bucket.unwrap();

        let endpoint = format!("https://{}.r2.cloudflarestorage.com", account);

        let creds = aws_sdk_s3::config::Credentials::new(
            access,
            secret,
            None,
            None,
            "tracera-r2",
        );

        let cfg = aws_sdk_s3::config::Builder::default()
            .endpoint_url(endpoint)
            .region(aws_sdk_s3::config::Region::new("auto"))
            .credentials_provider(creds)
            .behavior_version(aws_sdk_s3::config::BehaviorVersion::latest())
            .build();

        let client = aws_sdk_s3::Client::from_conf(cfg);

        info!("R2 artifact storage enabled (bucket: {})", bucket);
        Self {
            inner: Arc::new(R2Inner::Enabled { client, bucket }),
        }
    }

    pub fn is_enabled(&self) -> bool {
        matches!(*self.inner, R2Inner::Enabled { .. })
    }

    pub fn bucket(&self) -> Option<&str> {
        match &*self.inner {
            R2Inner::Disabled => None,
            R2Inner::Enabled { bucket, .. } => Some(bucket.as_str()),
        }
    }

    /// Upload `data` as `key` (e.g. `evidence/<id>.json`). Best-effort.
    pub async fn put_object(&self, key: &str, data: Vec<u8>, content_type: &str) {
        if let R2Inner::Enabled { client, bucket } = &*self.inner {
            use aws_sdk_s3::primitives::ByteStream;
            let body = ByteStream::from(data);
            let content_type = String::from(content_type);
            match client
                .put_object()
                .bucket(bucket)
                .key(key)
                .content_type(content_type)
                .body(body)
                .send()
                .await
            {
                Ok(_) => {}
                Err(e) => warn!("R2 put_object failed: {e:?}"),
            }
        }
    }

    /// Generate a presigned GET URL for `key` (e.g. for evidence download links).
    /// Returns None when storage is disabled.
    pub async fn presign_get(&self, key: &str, ttl_secs: u64) -> Option<String> {
        match &*self.inner {
            R2Inner::Disabled => None,
            R2Inner::Enabled { client, bucket } => {
                use aws_sdk_s3::presigning::PresigningConfig;
                let cfg = PresigningConfig::expires_in(std::time::Duration::from_secs(ttl_secs))
                    .expect("valid ttl");
                let presigned = client
                    .get_object()
                    .bucket(bucket)
                    .key(key)
                    .presigned(cfg)
                    .await
                    .ok()?;
                Some(presigned.uri().to_string())
            }
        }
    }
}
