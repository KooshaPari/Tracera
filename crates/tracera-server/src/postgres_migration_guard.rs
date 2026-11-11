use sqlx::migrate::Migrator;
use std::collections::BTreeSet;

pub(crate) static MIGRATOR: Migrator = sqlx::migrate!("./migrations-postgres");

pub(crate) fn duplicate_up_version(migrator: &Migrator) -> Option<i64> {
    let mut seen = BTreeSet::new();
    migrator
        .iter()
        .filter(|migration| !migration.migration_type.is_down_migration())
        .find_map(|migration| (!seen.insert(migration.version)).then_some(migration.version))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn embedded_manifest_duplicate_is_rejected() {
        assert_eq!(duplicate_up_version(&MIGRATOR), Some(11));
    }

    #[test]
    fn unique_and_injected_duplicate_controls() {
        let mut seen = BTreeSet::new();
        let mut migrations: Vec<_> = MIGRATOR
            .iter()
            .filter(|migration| {
                migration.migration_type.is_down_migration() || seen.insert(migration.version)
            })
            .cloned()
            .collect();
        assert_eq!(duplicate_up_version(&Migrator::with_migrations(migrations.clone())), None);
        let duplicate = migrations[0].clone();
        let version = duplicate.version;
        migrations.push(duplicate);
        assert_eq!(duplicate_up_version(&Migrator::with_migrations(migrations)), Some(version));
    }
}
