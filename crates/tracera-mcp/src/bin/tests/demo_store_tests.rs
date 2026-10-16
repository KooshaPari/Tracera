use super::DemoStore;
use tracera_server::item::{Item, ItemFilter};
use tracera_server::store::{Store, StoreError};

#[tokio::test]
async fn item_reads_report_unsupported_instead_of_empty_or_missing() {
    let store = DemoStore;
    assert!(matches!(
        store.list_items(ItemFilter::default(), 50, 0).await,
        Err(StoreError::UnsupportedOperation("DemoStore::list_items"))
    ));
    assert!(matches!(
        store.get_item("absent-item".into()).await,
        Err(StoreError::UnsupportedOperation("DemoStore::get_item"))
    ));
}

#[tokio::test]
async fn item_creation_reports_unsupported_instead_of_success() {
    let item = Item {
        id: "item-1".into(),
        project_id: "project-1".into(),
        view: "requirements".into(),
        item_type: "requirement".into(),
        title: "Must persist".into(),
        status: "open".into(),
        priority: "high".into(),
        version: 1,
        created_at: "2026-10-16T00:00:00Z".into(),
        updated_at: "2026-10-16T00:00:00Z".into(),
        extra: Default::default(),
    };
    assert!(matches!(
        DemoStore.create_item(item).await,
        Err(StoreError::UnsupportedOperation("DemoStore::create_item"))
    ));
}
