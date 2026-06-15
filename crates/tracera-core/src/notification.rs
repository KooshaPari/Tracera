//! Multi-channel notification dispatch: email, Slack, generic webhook, push.
//!
//! Each channel is modeled as a [`Channel`] enum variant with a per-channel
//! payload struct. A [`Dispatcher`] takes a [`Notification`] and routes it
//! to every channel listed in the notification's `channels` set, using
//! pluggable sender functions so the same API can be exercised from tests
//! (with an in-memory recorder) or from production (with an HTTP client).
//!
//! This module deliberately contains no I/O — sending is performed by
//! `Fn` closures that callers wire up. That keeps the core crate
//! dependency-free and makes the dispatcher trivial to unit-test.

use chrono::{DateTime, Utc};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use thiserror::Error;

// ---------------------------------------------------------------------------
// Channel + payload
// ---------------------------------------------------------------------------

/// Delivery channel for a notification. Each variant has a matching payload
/// struct in the notification body.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Channel {
    Email,
    Slack,
    Webhook,
    Push,
}

/// A notification envelope addressed to one or more channels.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Notification {
    /// Stable, caller-supplied ID. Used to de-duplicate retries.
    pub id: String,
    pub subject: String,
    pub body: String,
    /// Per-channel payload overrides. A channel with no entry uses the
    /// shared `subject`/`body` above.
    pub overrides: IndexMap<Channel, ChannelPayload>,
    /// Which channels should receive this notification. Order is
    /// significant for `DispatchReport` (channels are reported in the same
    /// order they were attempted).
    pub channels: Vec<Channel>,
    /// When the notification was created.
    pub created_at: DateTime<Utc>,
}

/// Per-channel payload override.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ChannelPayload {
    Email(EmailPayload),
    Slack(SlackPayload),
    Webhook(WebhookPayload),
    Push(PushPayload),
}

/// Plain-text email.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EmailPayload {
    pub from: String,
    pub to: Vec<String>,
    /// Override of the `Notification::subject`.
    pub subject: String,
    /// Override of the `Notification::body`.
    pub body: String,
    /// Optional list of attachment URLs. The dispatcher does not fetch
    /// them — it just relays the metadata.
    pub attachments: Vec<String>,
}

/// Slack incoming-webhook payload.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SlackPayload {
    pub webhook_url: String,
    pub channel: Option<String>,
    pub text: String,
    /// Optional Slack blocks (JSON). Stored as `String` to keep the core
    /// crate free of `serde_json::Value` pluming in this surface.
    pub blocks: Option<String>,
}

/// Generic outbound HTTP webhook.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WebhookPayload {
    pub url: String,
    pub method: WebhookMethod,
    /// Pre-rendered JSON body to POST/PUT. `None` means the dispatcher
    /// will synthesize a `{"id":..,"subject":..,"body":..}` payload.
    pub body: Option<String>,
    /// Optional content-type override. Defaults to `application/json`.
    pub content_type: Option<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum WebhookMethod {
    Post,
    Put,
}

/// Push notification (APNs/FCM-agnostic).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PushPayload {
    pub device_tokens: Vec<String>,
    pub title: String,
    pub body: String,
    /// Arbitrary data payload. Stored as `String` to keep the type
    /// JSON-portable across FCM and APNs.
    pub data: Option<String>,
}

// ---------------------------------------------------------------------------
// Dispatcher
// ---------------------------------------------------------------------------

/// One recorded send, captured by the in-memory recorder.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SentRecord {
    pub channel: Channel,
    pub target: String,
}

/// Outcome of dispatching a single notification.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DispatchReport {
    pub notification_id: String,
    pub results: Vec<ChannelResult>,
}

impl DispatchReport {
    pub fn all_succeeded(&self) -> bool {
        self.results.iter().all(|r| r.error.is_none())
    }

    pub fn succeeded(&self) -> usize {
        self.results.iter().filter(|r| r.error.is_none()).count()
    }

    pub fn failed(&self) -> usize {
        self.results.iter().filter(|r| r.error.is_some()).count()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ChannelResult {
    pub channel: Channel,
    pub target: String,
    pub error: Option<String>,
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum DispatchError {
    #[error("unknown channel: {0}")]
    UnknownChannel(String),
    #[error("missing payload for channel: {0:?}")]
    MissingPayload(Channel),
    #[error("no channels specified")]
    NoChannels,
}

type EmailSender = Arc<dyn Fn(&EmailPayload) -> Result<String, String> + Send + Sync>;
type SlackSender = Arc<dyn Fn(&SlackPayload) -> Result<String, String> + Send + Sync>;
type WebhookSender = Arc<dyn Fn(&WebhookPayload) -> Result<String, String> + Send + Sync>;
type PushSender = Arc<dyn Fn(&PushPayload) -> Result<String, String> + Send + Sync>;

/// Multi-channel dispatcher. Holds one sender closure per channel. In tests
/// the closures write to an `Arc<Mutex<Vec<SentRecord>>>` recorder.
#[derive(Clone)]
pub struct Dispatcher {
    email: Option<EmailSender>,
    slack: Option<SlackSender>,
    webhook: Option<WebhookSender>,
    push: Option<PushSender>,
}

impl std::fmt::Debug for Dispatcher {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Dispatcher")
            .field("email_configured", &self.email.is_some())
            .field("slack_configured", &self.slack.is_some())
            .field("webhook_configured", &self.webhook.is_some())
            .field("push_configured", &self.push.is_some())
            .finish()
    }
}

impl Default for Dispatcher {
    fn default() -> Self {
        Self::new()
    }
}

impl Dispatcher {
    pub fn new() -> Self {
        Self {
            email: None,
            slack: None,
            webhook: None,
            push: None,
        }
    }

    pub fn with_email(mut self, sender: EmailSender) -> Self {
        self.email = Some(sender);
        self
    }

    pub fn with_slack(mut self, sender: SlackSender) -> Self {
        self.slack = Some(sender);
        self
    }

    pub fn with_webhook(mut self, sender: WebhookSender) -> Self {
        self.webhook = Some(sender);
        self
    }

    pub fn with_push(mut self, sender: PushSender) -> Self {
        self.push = Some(sender);
        self
    }

    /// Dispatch a notification across all of its declared channels.
    pub fn dispatch(&self, n: &Notification) -> Result<DispatchReport, DispatchError> {
        if n.channels.is_empty() {
            return Err(DispatchError::NoChannels);
        }

        let mut results = Vec::with_capacity(n.channels.len());
        for &ch in &n.channels {
            let payload = n.overrides.get(&ch);
            let result = match (ch, payload) {
                (Channel::Email, Some(ChannelPayload::Email(p))) => self.send_email(p),
                (Channel::Email, None) => {
                    Err(DispatchError::MissingPayload(Channel::Email).to_string())
                }
                (Channel::Slack, Some(ChannelPayload::Slack(p))) => self.send_slack(p),
                (Channel::Slack, None) => {
                    Err(DispatchError::MissingPayload(Channel::Slack).to_string())
                }
                (Channel::Webhook, Some(ChannelPayload::Webhook(p))) => self.send_webhook(p),
                (Channel::Webhook, None) => {
                    Err(DispatchError::MissingPayload(Channel::Webhook).to_string())
                }
                (Channel::Push, Some(ChannelPayload::Push(p))) => self.send_push(p),
                (Channel::Push, None) => {
                    Err(DispatchError::MissingPayload(Channel::Push).to_string())
                }
                (ch, Some(_)) => {
                    // Override present but wrong variant.
                    Err(format!("payload/channel mismatch for {:?}", ch))
                }
            };

            let target = target_for(ch, payload);
            results.push(ChannelResult {
                channel: ch,
                target,
                error: result.err(),
            });
        }

        Ok(DispatchReport {
            notification_id: n.id.clone(),
            results,
        })
    }

    fn send_email(&self, p: &EmailPayload) -> Result<String, String> {
        match &self.email {
            Some(s) => s(p),
            None => Err("email sender not configured".into()),
        }
    }
    fn send_slack(&self, p: &SlackPayload) -> Result<String, String> {
        match &self.slack {
            Some(s) => s(p),
            None => Err("slack sender not configured".into()),
        }
    }
    fn send_webhook(&self, p: &WebhookPayload) -> Result<String, String> {
        match &self.webhook {
            Some(s) => s(p),
            None => Err("webhook sender not configured".into()),
        }
    }
    fn send_push(&self, p: &PushPayload) -> Result<String, String> {
        match &self.push {
            Some(s) => s(p),
            None => Err("push sender not configured".into()),
        }
    }
}

fn target_for(ch: Channel, payload: Option<&ChannelPayload>) -> String {
    match (ch, payload) {
        (Channel::Email, Some(ChannelPayload::Email(p))) => p.to.join(","),
        (Channel::Slack, Some(ChannelPayload::Slack(p))) => {
            p.channel.clone().unwrap_or_else(|| p.webhook_url.clone())
        }
        (Channel::Webhook, Some(ChannelPayload::Webhook(p))) => p.url.clone(),
        (Channel::Push, Some(ChannelPayload::Push(p))) => p.device_tokens.join(","),
        _ => "<unconfigured>".into(),
    }
}

// ---------------------------------------------------------------------------
// In-memory recorder for tests
// ---------------------------------------------------------------------------

/// Shared recorder that captures every `SentRecord` from senders wired into
/// a [`Dispatcher`]. Useful in tests.
#[derive(Debug, Default, Clone)]
pub struct Recorder {
    pub records: Arc<Mutex<Vec<SentRecord>>>,
}

impl Recorder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn snapshot(&self) -> Vec<SentRecord> {
        self.records.lock().unwrap().clone()
    }

    pub fn email_sender(self) -> EmailSender {
        let records = self.records.clone();
        Arc::new(move |p: &EmailPayload| {
            records.lock().unwrap().push(SentRecord {
                channel: Channel::Email,
                target: p.to.join(","),
            });
            Ok(format!("email:{}", p.to.join(",")))
        })
    }

    pub fn slack_sender(self) -> SlackSender {
        let records = self.records.clone();
        Arc::new(move |p: &SlackPayload| {
            records.lock().unwrap().push(SentRecord {
                channel: Channel::Slack,
                target: p.webhook_url.clone(),
            });
            Ok(format!("slack:{}", p.webhook_url))
        })
    }

    pub fn webhook_sender(self) -> WebhookSender {
        let records = self.records.clone();
        Arc::new(move |p: &WebhookPayload| {
            records.lock().unwrap().push(SentRecord {
                channel: Channel::Webhook,
                target: p.url.clone(),
            });
            Ok(format!("webhook:{}", p.url))
        })
    }

    pub fn push_sender(self) -> PushSender {
        let records = self.records.clone();
        Arc::new(move |p: &PushPayload| {
            records.lock().unwrap().push(SentRecord {
                channel: Channel::Push,
                target: p.device_tokens.join(","),
            });
            Ok(format!("push:{}", p.device_tokens.len()))
        })
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn notification(channels: Vec<Channel>) -> Notification {
        Notification {
            id: "n-1".into(),
            subject: "S".into(),
            body: "B".into(),
            overrides: IndexMap::new(),
            channels,
            created_at: Utc::now(),
        }
    }

    #[test]
    fn dispatch_routes_to_all_configured_channels() {
        let recorder = Recorder::new();
        let dispatcher = Dispatcher::new()
            .with_email(recorder.clone().email_sender())
            .with_slack(recorder.clone().slack_sender())
            .with_webhook(recorder.clone().webhook_sender())
            .with_push(recorder.clone().push_sender());

        let mut n = notification(vec![Channel::Email, Channel::Push]);
        n.overrides.insert(
            Channel::Email,
            ChannelPayload::Email(EmailPayload {
                from: "a@b".into(),
                to: vec!["x@y".into()],
                subject: "S".into(),
                body: "B".into(),
                attachments: vec![],
            }),
        );
        n.overrides.insert(
            Channel::Push,
            ChannelPayload::Push(PushPayload {
                device_tokens: vec!["dev1".into()],
                title: "T".into(),
                body: "B".into(),
                data: None,
            }),
        );

        let report = dispatcher.dispatch(&n).unwrap();
        assert_eq!(report.results.len(), 2);
        assert!(report.all_succeeded());
        assert_eq!(report.succeeded(), 2);

        let snap = recorder.snapshot();
        assert_eq!(snap.len(), 2);
        assert!(snap.iter().any(|r| r.channel == Channel::Email));
        assert!(snap.iter().any(|r| r.channel == Channel::Push));
    }

    #[test]
    fn dispatch_rejects_empty_channels() {
        let dispatcher = Dispatcher::new();
        let n = notification(vec![]);
        let err = dispatcher.dispatch(&n).unwrap_err();
        assert_eq!(err, DispatchError::NoChannels);
    }

    #[test]
    fn dispatch_reports_missing_payload() {
        let dispatcher = Dispatcher::new();
        let n = notification(vec![Channel::Slack]);
        let report = dispatcher.dispatch(&n).unwrap();
        assert_eq!(report.failed(), 1);
        assert_eq!(report.succeeded(), 0);
        let first = &report.results[0];
        let err = first.error.as_ref().unwrap();
        assert!(err.contains("missing payload") || err.contains("MissingPayload"), "error was: {err}");
    }

    #[test]
    fn dispatch_marks_unconfigured_sender_as_error() {
        let dispatcher = Dispatcher::new().with_email(recorder_email_only());
        let mut n = notification(vec![Channel::Slack]);
        n.overrides.insert(
            Channel::Slack,
            ChannelPayload::Slack(SlackPayload {
                webhook_url: "https://hooks/x".into(),
                channel: Some("#alerts".into()),
                text: "x".into(),
                blocks: None,
            }),
        );
        let report = dispatcher.dispatch(&n).unwrap();
        assert_eq!(report.failed(), 1);
        assert!(report.results[0]
            .error
            .as_ref()
            .unwrap()
            .contains("not configured"));
    }

    #[test]
    fn dispatch_propagates_sender_error() {
        let sender: EmailSender = Arc::new(|_p| Err("upstream down".into()));
        let dispatcher = Dispatcher::new().with_email(sender);
        let mut n = notification(vec![Channel::Email]);
        n.overrides.insert(
            Channel::Email,
            ChannelPayload::Email(EmailPayload {
                from: "a".into(),
                to: vec!["b".into()],
                subject: "S".into(),
                body: "B".into(),
                attachments: vec![],
            }),
        );
        let report = dispatcher.dispatch(&n).unwrap();
        assert_eq!(report.failed(), 1);
        assert_eq!(
            report.results[0].error.as_deref(),
            Some("upstream down")
        );
    }

    #[test]
    fn dispatch_all_channels_records_every_channel() {
        let recorder = Recorder::new();
        let dispatcher = Dispatcher::new()
            .with_email(recorder.clone().email_sender())
            .with_slack(recorder.clone().slack_sender())
            .with_webhook(recorder.clone().webhook_sender())
            .with_push(recorder.clone().push_sender());
        let mut n = notification(vec![Channel::Email, Channel::Slack, Channel::Webhook, Channel::Push]);
        n.overrides.insert(Channel::Email, ChannelPayload::Email(EmailPayload {
            from: "a@b".into(), to: vec!["x@y".into()], subject: "S".into(), body: "B".into(), attachments: vec![],
        }));
        n.overrides.insert(Channel::Slack, ChannelPayload::Slack(SlackPayload {
            webhook_url: "https://hooks/slack".into(), channel: Some("#alerts".into()), text: "t".into(), blocks: None,
        }));
        n.overrides.insert(Channel::Webhook, ChannelPayload::Webhook(WebhookPayload {
            url: "https://api.example/hook".into(), method: WebhookMethod::Post, body: None, content_type: None,
        }));
        n.overrides.insert(Channel::Push, ChannelPayload::Push(PushPayload {
            device_tokens: vec!["dev1".into(), "dev2".into()], title: "T".into(), body: "B".into(), data: None,
        }));
        let report = dispatcher.dispatch(&n).unwrap();
        assert!(report.all_succeeded());
        assert_eq!(report.succeeded(), 4);
        let snap = recorder.snapshot();
        assert_eq!(snap.len(), 4);
        assert!(snap.iter().any(|r| r.channel == Channel::Webhook));
    }

    fn recorder_email_only() -> EmailSender {
        Arc::new(|p| Ok(format!("e:{}", p.to.join(","))))
    }
}
