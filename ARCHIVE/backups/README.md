# Backup Consolidation Summary

## Overview
This directory contains consolidated and organized backup files for the TracerTM system.

## Directory Structure
```
backups/
├── README.md              # This file
├── MANIFEST.json          # Detailed metadata for all backups
├── archive/               # Directory containing all backup files
│   ├── INDEX.json         # Quick index of archived files
│   └── tracertm_backup_*.json.gz  # 201 backup files
└── manifest/              # Reserved for additional manifest files
```

## Consolidation Summary

### Statistics
- **Total Backups Consolidated**: 201 files
- **Total Storage Size**: 60M
- **Date Range**: 2025-12-02 18:58:10 to 2025-12-03 22:47:08
- **Time Span**: ~1 day

### File Categories
All backups follow the naming convention: `tracertm_backup_YYYYMMDD_HHMMSS.json.gz`
- **Purpose**: System backup (automatic backups of TracerTM state)
- **Format**: gzip-compressed JSON
- **Size Range**: 155B - 444K per file

## File Locations

### MANIFEST.json
Located at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/MANIFEST.json`

Contains:
- Complete list of all 201 backup files
- Individual file sizes (in bytes and display format)
- Timestamps and human-readable dates
- Purpose classification
- Summary statistics

### Archive Directory
Located at: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/archive/`

Contains:
- All 201 compressed backup files
- INDEX.json for quick file listing
- Total size: 60M

## How to Use

### View All Backups
```bash
cat /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/MANIFEST.json | jq '.'
```

### List Backup Files
```bash
ls /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/archive/
```

### Access Specific Backup
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/archive/
gunzip -c tracertm_backup_20251203_224708.json.gz | jq '.'
```

### Get Archive Statistics
```bash
du -sh /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/archive/
find /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/archive -name "*.json.gz" | wc -l
```

## Notes

- All original backup files have been moved (not copied) to the archive directory
- No backups were deleted; all 201 files are safely stored
- The manifest provides complete metadata for recovery or analysis
- Archive files are organized by timestamp (chronological order)

## Manifest Format

Each backup entry in MANIFEST.json includes:
```json
{
  "filename": "tracertm_backup_20251203_224708.json.gz",
  "timestamp": "20251203_224708",
  "date": "2025-12-03 22:47:08",
  "size_bytes": 453632,
  "size_display": "444K",
  "path": "/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backups/archive/tracertm_backup_20251203_224708.json.gz",
  "purpose": "system_backup"
}
```

---
*Backup consolidation completed on 2025-12-04*
