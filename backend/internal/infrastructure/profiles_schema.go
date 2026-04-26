// Package infrastructure wires infrastructure dependencies.
package infrastructure

import (
	"fmt"

	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func migrateAuthProfilesSchema(gormDB *gorm.DB) error {
	// One-time migration: old schema had workos_id NOT NULL; GORM model uses workos_user_id only.
	// Try RENAME; if workos_user_id already exists (both columns), DROP workos_id instead.
	// To run manually: psql $DATABASE_URL -f migrations/20260131_profiles_workos_id.sql
	_ = gormDB.Exec(`DO $$ BEGIN
		IF EXISTS (SELECT 1 FROM information_schema.columns
			WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'workos_id') THEN
			BEGIN
				ALTER TABLE public.profiles RENAME COLUMN workos_id TO workos_user_id;
			EXCEPTION
				WHEN duplicate_column THEN
					ALTER TABLE public.profiles DROP COLUMN workos_id;
				WHEN undefined_column THEN
					NULL;
			END;
		END IF;
	END $$`).Error

	for _, schema := range []string{"public", "tracertm"} {
		if err := prepareProfileEmailConstraint(gormDB, schema); err != nil {
			return err
		}
	}
	if err := gormDB.AutoMigrate(&models.Profile{}); err != nil {
		return fmt.Errorf("failed to auto-migrate profiles: %w", err)
	}
	for _, schema := range []string{"public", "tracertm"} {
		_ = dropProfileEmailConstraint(gormDB, schema)
	}
	return nil
}

func prepareProfileEmailConstraint(gormDB *gorm.DB, schema string) error {
	err := gormDB.Exec(fmt.Sprintf(`DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = '%s' AND table_name = 'profiles'
  ) AND NOT EXISTS (
    SELECT 1 FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = '%s' AND t.relname = 'profiles' AND c.conname = 'uni_profiles_email'
  ) THEN
    ALTER TABLE %s.profiles ADD CONSTRAINT uni_profiles_email UNIQUE (email);
  END IF;
EXCEPTION
  WHEN undefined_table THEN NULL;
  WHEN invalid_schema_name THEN NULL;
END $$`, schema, schema, schema)).Error
	if err != nil {
		return fmt.Errorf("failed to prepare %s.profiles email uniqueness for automigrate: %w", schema, err)
	}
	return nil
}

func dropProfileEmailConstraint(gormDB *gorm.DB, schema string) error {
	return gormDB.Exec(fmt.Sprintf(`DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = '%s' AND table_name = 'profiles'
  ) THEN
    ALTER TABLE %s.profiles DROP CONSTRAINT IF EXISTS uni_profiles_email;
  END IF;
EXCEPTION
  WHEN undefined_table THEN NULL;
  WHEN invalid_schema_name THEN NULL;
END $$`, schema, schema)).Error
}
