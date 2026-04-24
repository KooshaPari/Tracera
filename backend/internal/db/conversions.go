// Package db provides db functionality.
package db

// GetItemRowFromIDsRow converts ListItemsByIDsRow to GetItemRow
// Both types have identical structures, so this is a simple direct conversion
func GetItemRowFromIDsRow(item ListItemsByIDsRow) GetItemRow {
	return GetItemRow(item)
}

// GetItemRowFromProjectRow converts ListItemsByProjectRow to GetItemRow
func GetItemRowFromProjectRow(item ListItemsByProjectRow) GetItemRow {
	return GetItemRow(item)
}

// GetItemRowFromOrphanRow converts GetOrphanItemsRow to GetItemRow
func GetItemRowFromOrphanRow(item GetOrphanItemsRow) GetItemRow {
	return GetItemRow(item)
}
