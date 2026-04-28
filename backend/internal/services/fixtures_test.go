//go:build !integration && !e2e

package services

import "github.com/google/uuid"

// Shared test fixtures for services package
var (
	testItem1ID           = uuid.New().String()
	testItemID            = uuid.New().String()
	testProjectIDValue    = uuid.New().String()
	testViewID            = uuid.New().String()
	testNonexistentID     = uuid.New().String()
	testSnapshotSessionID = uuid.New().String()
)
