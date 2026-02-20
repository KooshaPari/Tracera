package services

// This file contains example usage patterns for TransactionContext
// These examples are provided for documentation purposes

/*
Example 1: Basic Transaction Propagation
=========================================

func (s *ItemServiceImpl) CreateItemWithLinks(ctx context.Context, item *models.Item, links []*models.Link) error {
	// Start a transaction
	tx := s.db.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	// Add transaction to context
	txCtx := WithTransaction(ctx, tx)

	// Create the item (repository will use the transaction from context)
	if err := s.itemRepo.Create(txCtx, item); err != nil {
		tx.Rollback()
		return err
	}

	// Create all links in the same transaction
	for _, link := range links {
		if err := s.linkRepo.Create(txCtx, link); err != nil {
			tx.Rollback()
			return err
		}
	}

	// Commit the transaction
	return tx.Commit().Error
}


Example 2: Cross-Service Transaction
====================================

func (s *ProjectServiceImpl) CreateProjectWithItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	// Start a transaction
	tx := s.db.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	// Add transaction to context
	txCtx := WithTransaction(ctx, tx)

	// Create the project
	if err := s.projectRepo.Create(txCtx, project); err != nil {
		tx.Rollback()
		return err
	}

	// Use ItemService to create items (it will use the same transaction)
	for _, item := range items {
		item.ProjectID = project.ID
		if err := s.itemService.CreateItem(txCtx, item); err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}


Example 3: Repository Using GetDB Helper
========================================

// In repository implementation
func (r *itemRepository) Create(ctx context.Context, item *models.Item) error {
	// GetDB will return the transaction if present, otherwise the fallback DB
	db := GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(item).Error
}

func (r *itemRepository) Update(ctx context.Context, item *models.Item) error {
	db := GetDB(ctx, r.db)
	return db.WithContext(ctx).Save(item).Error
}


Example 4: Nested Service Calls
================================

func (s *CrossServiceImpl) MoveItemToProject(ctx context.Context, itemID, newProjectID string) error {
	tx := s.db.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	txCtx := WithTransaction(ctx, tx)

	// Get the item
	item, err := s.itemService.GetItem(txCtx, itemID)
	if err != nil {
		tx.Rollback()
		return err
	}

	// Delete old links
	if err := s.linkService.DeleteByItemID(txCtx, itemID); err != nil {
		tx.Rollback()
		return err
	}

	// Update the item
	item.ProjectID = newProjectID
	if err := s.itemService.UpdateItem(txCtx, item); err != nil {
		tx.Rollback()
		return err
	}

	// Create new project link
	link := &models.Link{
		SourceID: newProjectID,
		TargetID: itemID,
		Type:     "project_item",
	}
	if err := s.linkService.CreateLink(txCtx, link); err != nil {
		tx.Rollback()
		return err
	}

	return tx.Commit().Error
}


Example 5: Check Before Starting Transaction
============================================

func (s *ItemServiceImpl) UpdateItemSafely(ctx context.Context, item *models.Item) error {
	// Check if we're already in a transaction
	if IsInTransaction(ctx) {
		// Just use the existing transaction
		return s.itemRepo.Update(ctx, item)
	}

	// Start a new transaction
	tx := s.db.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	txCtx := WithTransaction(ctx, tx)
	if err := s.itemRepo.Update(txCtx, item); err != nil {
		tx.Rollback()
		return err
	}

	return tx.Commit().Error
}


Example 6: GORM Transaction Helper
==================================

func (s *ItemServiceImpl) CreateItemInTransaction(ctx context.Context, item *models.Item) error {
	// Using GORM's built-in Transaction helper
	return s.db.Transaction(func(tx *gorm.DB) error {
		// Add transaction to context
		txCtx := WithTransaction(ctx, tx)

		// All operations in this function will use the same transaction
		if err := s.itemRepo.Create(txCtx, item); err != nil {
			return err // GORM will rollback automatically
		}

		// Publish event
		if s.natsConn != nil {
			data, _ := json.Marshal(item)
			s.natsConn.Publish("items.created", data)
		}

		return nil // GORM will commit automatically
	})
}


Example 7: Context-Aware Repository
===================================

// Repository that automatically uses transaction from context
func (r *itemRepository) execInContext(ctx context.Context, fn func(*gorm.DB) error) error {
	// Get the appropriate DB connection
	db := GetDB(ctx, r.db)

	// Execute the function with context
	return fn(db.WithContext(ctx))
}

func (r *itemRepository) Create(ctx context.Context, item *models.Item) error {
	return r.execInContext(ctx, func(db *gorm.DB) error {
		return db.Create(item).Error
	})
}

func (r *itemRepository) Update(ctx context.Context, item *models.Item) error {
	return r.execInContext(ctx, func(db *gorm.DB) error {
		return db.Save(item).Error
	})
}


Example 8: Error Handling Pattern
=================================

func (s *ProjectServiceImpl) ComplexOperation(ctx context.Context, project *models.Project) error {
	tx := s.db.Begin()
	if tx.Error != nil {
		return fmt.Errorf("failed to begin transaction: %w", tx.Error)
	}

	// Use named return value for easier cleanup
	err := func() error {
		txCtx := WithTransaction(ctx, tx)

		if err := s.projectRepo.Create(txCtx, project); err != nil {
			return fmt.Errorf("failed to create project: %w", err)
		}

		if err := s.notifyProjectCreated(txCtx, project); err != nil {
			return fmt.Errorf("failed to send notification: %w", err)
		}

		return nil
	}()

	if err != nil {
		tx.Rollback()
		return err
	}

	return tx.Commit().Error
}
*/
