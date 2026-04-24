/*
Phase 7 pgx refactoring - Work in Progress

This file will contain pgx/sqlc-based repository implementations.
Currently in progress - type conversion helpers needed for:

1. Priority: int32 (DB) ↔ string (models)
   - Need mapping: 0->low, 1->medium, 2->high
   - Or keep as string encoding in DB

2. Timestamps: pgtype.Timestamp ↔ *time.Time (nullable)
   - Handle NULL values from deleted_at
   - Convert to/from time.Time pointers

3. Text fields: pgtype.Text ↔ string
   - Handle NULL values
   - Empty string vs NULL distinction

Status: Framework established, utility functions ready
Next Step: Implement type adapters and test with Phase 7 integration tests

Completion will allow gradual migration from GORM while maintaining
backward compatibility through the repository interfaces.

Implementation Strategy:
1. Create type adapter functions (priority, timestamp, text)
2. Implement one repository fully (e.g., ItemRepository)
3. Test with Phase 7.4 integration tests
4. Migrate other repositories incrementally
5. Eventually remove GORM dependency for these repositories
*/

package repository

// Note: Type adapters not yet implemented

// adaptPriority converts between string (models) and int32 (DB)
// func adaptPriority(s string) int32
// func adaptPriorityFromDB(i int32) string

// adaptTimestamp converts between *time.Time (models) and pgtype.Timestamp (DB)
// func adaptTimestamp(t *time.Time) pgtype.Timestamp
// func adaptTimestampFromDB(pt pgtype.Timestamp) *time.Time

// adaptText converts between string (models) and pgtype.Text (DB)
// func adaptText(s string) pgtype.Text
// func adaptTextFromDB(pt pgtype.Text) string
