# H. Adoption: Load the Hand Corpus into AgilePlus, Portal, and Tracera

**Phase:** P8 (Adoption)  
**Task Prefix:** AD-001..AD-100  
**Goal:** Load this corpus after AgilePlus can store it and Portal can show it. The witness status stays open until a real restart witness exists.  
**Depends On:** P3, P4, P6, P7  
**Unlocks:** none

Each surface is one real gap. The four leaves on a surface are record, contract, change, and proof. They are not index clones.

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|------------|-----|---------|------------|
| AD-001 | Record: import is refused while the daemon binary is missing | — | 10m | agileplus-mcpd binary | Current behavior is written down with the command or query used |
| AD-002 | Contract: import is refused while the daemon binary is missing | AD-001 | 10m | agileplus-mcpd binary | Expected behavior is stated as a pass/fail check |
| AD-003 | Change: import is refused while the daemon binary is missing | AD-002 | 20m | agileplus-mcpd binary | The surface matches the contract or the gap is recorded as still open |
| AD-004 | Prove: import is refused while the daemon binary is missing | AD-003 | 10m | agileplus-mcpd binary | The check fails on the broken input and passes on the fixed input |
| AD-005 | Record: import is refused while list crashes on timestamp conversion | — | 10m | agileplus list SQLite timestamp | Current behavior is written down with the command or query used |
| AD-006 | Contract: import is refused while list crashes on timestamp conversion | AD-005 | 10m | agileplus list SQLite timestamp | Expected behavior is stated as a pass/fail check |
| AD-007 | Change: import is refused while list crashes on timestamp conversion | AD-006 | 20m | agileplus list SQLite timestamp | The surface matches the contract or the gap is recorded as still open |
| AD-008 | Prove: import is refused while list crashes on timestamp conversion | AD-007 | 10m | agileplus list SQLite timestamp | The check fails on the broken input and passes on the fixed input |
| AD-009 | Record: the skill commands are aligned with the installed CLI before import | — | 10m | AgilePlus skill CLI versus real CLI | Current behavior is written down with the command or query used |
| AD-010 | Contract: the skill commands are aligned with the installed CLI before import | AD-009 | 10m | AgilePlus skill CLI versus real CLI | Expected behavior is stated as a pass/fail check |
| AD-011 | Change: the skill commands are aligned with the installed CLI before import | AD-010 | 20m | AgilePlus skill CLI versus real CLI | The surface matches the contract or the gap is recorded as still open |
| AD-012 | Prove: the skill commands are aligned with the installed CLI before import | AD-011 | 10m | AgilePlus skill CLI versus real CLI | The check fails on the broken input and passes on the fixed input |
| AD-013 | Record: each repo work package is a row in the crosswalk, including ones with no docs-5 match | — | 10m | repo WP-00..WP-25 | Current behavior is written down with the command or query used |
| AD-014 | Contract: each repo work package is a row in the crosswalk, including ones with no docs-5 match | AD-013 | 10m | repo WP-00..WP-25 | Expected behavior is stated as a pass/fail check |
| AD-015 | Change: each repo work package is a row in the crosswalk, including ones with no docs-5 match | AD-014 | 20m | repo WP-00..WP-25 | The surface matches the contract or the gap is recorded as still open |
| AD-016 | Prove: each repo work package is a row in the crosswalk, including ones with no docs-5 match | AD-015 | 10m | repo WP-00..WP-25 | The check fails on the broken input and passes on the fixed input |
| AD-017 | Record: each WP-T title from docs-5/work/WBS.md is a row in the crosswalk | — | 10m | docs-5 WP-T01..WP-T11 | Current behavior is written down with the command or query used |
| AD-018 | Contract: each WP-T title from docs-5/work/WBS.md is a row in the crosswalk | AD-017 | 10m | docs-5 WP-T01..WP-T11 | Expected behavior is stated as a pass/fail check |
| AD-019 | Change: each WP-T title from docs-5/work/WBS.md is a row in the crosswalk | AD-018 | 20m | docs-5 WP-T01..WP-T11 | The surface matches the contract or the gap is recorded as still open |
| AD-020 | Prove: each WP-T title from docs-5/work/WBS.md is a row in the crosswalk | AD-019 | 10m | docs-5 WP-T01..WP-T11 | The check fails on the broken input and passes on the fixed input |
| AD-021 | Record: each spec-014 package is a row, including ones with no repo match | AD-020 | 10m | AgilePlus spec 014 WP-000..WP-018 | Current behavior is written down with the command or query used |
| AD-022 | Contract: each spec-014 package is a row, including ones with no repo match | AD-021 | 10m | AgilePlus spec 014 WP-000..WP-018 | Expected behavior is stated as a pass/fail check |
| AD-023 | Change: each spec-014 package is a row, including ones with no repo match | AD-022 | 20m | AgilePlus spec 014 WP-000..WP-018 | The surface matches the contract or the gap is recorded as still open |
| AD-024 | Prove: each spec-014 package is a row, including ones with no repo match | AD-023 | 10m | AgilePlus spec 014 WP-000..WP-018 | The check fails on the broken input and passes on the fixed input |
| AD-025 | Record: a missing equivalence stays an open resolve-task and is not guessed | — | 10m | crosswalk unknown cells | Current behavior is written down with the command or query used |
| AD-026 | Contract: a missing equivalence stays an open resolve-task and is not guessed | AD-025 | 10m | crosswalk unknown cells | Expected behavior is stated as a pass/fail check |
| AD-027 | Change: a missing equivalence stays an open resolve-task and is not guessed | AD-026 | 20m | crosswalk unknown cells | The surface matches the contract or the gap is recorded as still open |
| AD-028 | Prove: a missing equivalence stays an open resolve-task and is not guessed | AD-027 | 10m | crosswalk unknown cells | The check fails on the broken input and passes on the fixed input |
| AD-029 | Record: this folder is the import source | — | 10m | session corpus 20261015-e2e-optimality | Current behavior is written down with the command or query used |
| AD-030 | Contract: this folder is the import source | AD-029 | 10m | session corpus 20261015-e2e-optimality | Expected behavior is stated as a pass/fail check |
| AD-031 | Change: this folder is the import source | AD-030 | 20m | session corpus 20261015-e2e-optimality | The surface matches the contract or the gap is recorded as still open |
| AD-032 | Prove: this folder is the import source | AD-031 | 10m | session corpus 20261015-e2e-optimality | The check fails on the broken input and passes on the fixed input |
| AD-033 | Record: importing the same corpus twice does not duplicate records | — | 10m | AgilePlus re-import | Current behavior is written down with the command or query used |
| AD-034 | Contract: importing the same corpus twice does not duplicate records | AD-033 | 10m | AgilePlus re-import | Expected behavior is stated as a pass/fail check |
| AD-035 | Change: importing the same corpus twice does not duplicate records | AD-034 | 20m | AgilePlus re-import | The surface matches the contract or the gap is recorded as still open |
| AD-036 | Prove: importing the same corpus twice does not duplicate records | AD-035 | 10m | AgilePlus re-import | The check fails on the broken input and passes on the fixed input |
| AD-037 | Record: the dossier gains a pointer to this folder | — | 10m | docs-5 products/Tracera/DOSSIER.md | Current behavior is written down with the command or query used |
| AD-038 | Contract: the dossier gains a pointer to this folder | AD-037 | 10m | docs-5 products/Tracera/DOSSIER.md | Expected behavior is stated as a pass/fail check |
| AD-039 | Change: the dossier gains a pointer to this folder | AD-038 | 20m | docs-5 products/Tracera/DOSSIER.md | The surface matches the contract or the gap is recorded as still open |
| AD-040 | Prove: the dossier gains a pointer to this folder | AD-039 | 10m | docs-5 products/Tracera/DOSSIER.md | The check fails on the broken input and passes on the fixed input |
| AD-041 | Record: no second writable RTM is created there | AD-040 | 10m | docs-5 products/Tracera/architecture/ | Current behavior is written down with the command or query used |
| AD-042 | Contract: no second writable RTM is created there | AD-041 | 10m | docs-5 products/Tracera/architecture/ | Expected behavior is stated as a pass/fail check |
| AD-043 | Change: no second writable RTM is created there | AD-042 | 20m | docs-5 products/Tracera/architecture/ | The surface matches the contract or the gap is recorded as still open |
| AD-044 | Prove: no second writable RTM is created there | AD-043 | 10m | docs-5 products/Tracera/architecture/ | The check fails on the broken input and passes on the fixed input |
| AD-045 | Record: Portal shows the imported task ids | — | 10m | job-cockpit imported-id view | Current behavior is written down with the command or query used |
| AD-046 | Contract: Portal shows the imported task ids | AD-045 | 10m | job-cockpit imported-id view | Expected behavior is stated as a pass/fail check |
| AD-047 | Change: Portal shows the imported task ids | AD-046 | 20m | job-cockpit imported-id view | The surface matches the contract or the gap is recorded as still open |
| AD-048 | Prove: Portal shows the imported task ids | AD-047 | 10m | job-cockpit imported-id view | The check fails on the broken input and passes on the fixed input |
| AD-049 | Record: AgilePlus records store the Paperclip project id | — | 10m | Paperclip project foreign keys | Current behavior is written down with the command or query used |
| AD-050 | Contract: AgilePlus records store the Paperclip project id | AD-049 | 10m | Paperclip project foreign keys | Expected behavior is stated as a pass/fail check |
| AD-051 | Change: AgilePlus records store the Paperclip project id | AD-050 | 20m | Paperclip project foreign keys | The surface matches the contract or the gap is recorded as still open |
| AD-052 | Prove: AgilePlus records store the Paperclip project id | AD-051 | 10m | Paperclip project foreign keys | The check fails on the broken input and passes on the fixed input |
| AD-053 | Record: those three issues are linked from the imported records | — | 10m | GitHub issues #1098 #1119 #1121 | Current behavior is written down with the command or query used |
| AD-054 | Contract: those three issues are linked from the imported records | AD-053 | 10m | GitHub issues #1098 #1119 #1121 | Expected behavior is stated as a pass/fail check |
| AD-055 | Change: those three issues are linked from the imported records | AD-054 | 20m | GitHub issues #1098 #1119 #1121 | The surface matches the contract or the gap is recorded as still open |
| AD-056 | Prove: those three issues are linked from the imported records | AD-055 | 10m | GitHub issues #1098 #1119 #1121 | The check fails on the broken input and passes on the fixed input |
| AD-057 | Record: the three witness actions are acceptance records, status open | — | 10m | CUR-1162254344-A1 A2 A3 | Current behavior is written down with the command or query used |
| AD-058 | Contract: the three witness actions are acceptance records, status open | AD-057 | 10m | CUR-1162254344-A1 A2 A3 | Expected behavior is stated as a pass/fail check |
| AD-059 | Change: the three witness actions are acceptance records, status open | AD-058 | 20m | CUR-1162254344-A1 A2 A3 | The surface matches the contract or the gap is recorded as still open |
| AD-060 | Prove: the three witness actions are acceptance records, status open | AD-059 | 10m | CUR-1162254344-A1 A2 A3 | The check fails on the broken input and passes on the fixed input |
| AD-061 | Record: the Tracera and AgilePlus reciprocal witness is one record | AD-060 | 10m | WP-FED-07 | Current behavior is written down with the command or query used |
| AD-062 | Contract: the Tracera and AgilePlus reciprocal witness is one record | AD-061 | 10m | WP-FED-07 | Expected behavior is stated as a pass/fail check |
| AD-063 | Change: the Tracera and AgilePlus reciprocal witness is one record | AD-062 | 20m | WP-FED-07 | The surface matches the contract or the gap is recorded as still open |
| AD-064 | Prove: the Tracera and AgilePlus reciprocal witness is one record | AD-063 | 10m | WP-FED-07 | The check fails on the broken input and passes on the fixed input |
| AD-065 | Record: each required adversarial vector is a test record | — | 10m | docs-5/qa/NEGATIVE-CONTROLS.md | Current behavior is written down with the command or query used |
| AD-066 | Contract: each required adversarial vector is a test record | AD-065 | 10m | docs-5/qa/NEGATIVE-CONTROLS.md | Expected behavior is stated as a pass/fail check |
| AD-067 | Change: each required adversarial vector is a test record | AD-066 | 20m | docs-5/qa/NEGATIVE-CONTROLS.md | The surface matches the contract or the gap is recorded as still open |
| AD-068 | Prove: each required adversarial vector is a test record | AD-067 | 10m | docs-5/qa/NEGATIVE-CONTROLS.md | The check fails on the broken input and passes on the fixed input |
| AD-069 | Record: each measurement family is a gate record at the 85% floor | — | 10m | docs-5/qa/METRICS.md MET-* | Current behavior is written down with the command or query used |
| AD-070 | Contract: each measurement family is a gate record at the 85% floor | AD-069 | 10m | docs-5/qa/METRICS.md MET-* | Expected behavior is stated as a pass/fail check |
| AD-071 | Change: each measurement family is a gate record at the 85% floor | AD-070 | 20m | docs-5/qa/METRICS.md MET-* | The surface matches the contract or the gap is recorded as still open |
| AD-072 | Prove: each measurement family is a gate record at the 85% floor | AD-071 | 10m | docs-5/qa/METRICS.md MET-* | The check fails on the broken input and passes on the fixed input |
| AD-073 | Record: the 26 pre-existing modifications are excluded from the import snapshot | — | 10m | Tracera dirty worktree | Current behavior is written down with the command or query used |
| AD-074 | Contract: the 26 pre-existing modifications are excluded from the import snapshot | AD-073 | 10m | Tracera dirty worktree | Expected behavior is stated as a pass/fail check |
| AD-075 | Change: the 26 pre-existing modifications are excluded from the import snapshot | AD-074 | 20m | Tracera dirty worktree | The surface matches the contract or the gap is recorded as still open |
| AD-076 | Prove: the 26 pre-existing modifications are excluded from the import snapshot | AD-075 | 10m | Tracera dirty worktree | The check fails on the broken input and passes on the fixed input |
| AD-077 | Record: the plan baseline is recorded as uncertified | — | 10m | git HEAD 191551f04 | Current behavior is written down with the command or query used |
| AD-078 | Contract: the plan baseline is recorded as uncertified | AD-077 | 10m | git HEAD 191551f04 | Expected behavior is stated as a pass/fail check |
| AD-079 | Change: the plan baseline is recorded as uncertified | AD-078 | 20m | git HEAD 191551f04 | The surface matches the contract or the gap is recorded as still open |
| AD-080 | Prove: the plan baseline is recorded as uncertified | AD-079 | 10m | git HEAD 191551f04 | The check fails on the broken input and passes on the fixed input |
| AD-081 | Record: the 190 false negatives and 14 false positives are re-measured after import | AD-080 | 10m | AgilePlus load check | Current behavior is written down with the command or query used |
| AD-082 | Contract: the 190 false negatives and 14 false positives are re-measured after import | AD-081 | 10m | AgilePlus load check | Expected behavior is stated as a pass/fail check |
| AD-083 | Change: the 190 false negatives and 14 false positives are re-measured after import | AD-082 | 20m | AgilePlus load check | The surface matches the contract or the gap is recorded as still open |
| AD-084 | Prove: the 190 false negatives and 14 false positives are re-measured after import | AD-083 | 10m | AgilePlus load check | The check fails on the broken input and passes on the fixed input |
| AD-085 | Record: spec 009 stays draft until the ingest it describes exists | — | 10m | AgilePlus spec 009 | Current behavior is written down with the command or query used |
| AD-086 | Contract: spec 009 stays draft until the ingest it describes exists | AD-085 | 10m | AgilePlus spec 009 | Expected behavior is stated as a pass/fail check |
| AD-087 | Change: spec 009 stays draft until the ingest it describes exists | AD-086 | 20m | AgilePlus spec 009 | The surface matches the contract or the gap is recorded as still open |
| AD-088 | Prove: spec 009 stays draft until the ingest it describes exists | AD-087 | 10m | AgilePlus spec 009 | The check fails on the broken input and passes on the fixed input |
| AD-089 | Record: the dropped Tracera work package is restored or explicitly retired | — | 10m | AgilePlus spec 020 tasks.md | Current behavior is written down with the command or query used |
| AD-090 | Contract: the dropped Tracera work package is restored or explicitly retired | AD-089 | 10m | AgilePlus spec 020 tasks.md | Expected behavior is stated as a pass/fail check |
| AD-091 | Change: the dropped Tracera work package is restored or explicitly retired | AD-090 | 20m | AgilePlus spec 020 tasks.md | The surface matches the contract or the gap is recorded as still open |
| AD-092 | Prove: the dropped Tracera work package is restored or explicitly retired | AD-091 | 10m | AgilePlus spec 020 tasks.md | The check fails on the broken input and passes on the fixed input |
| AD-093 | Record: the spec-only absorption package is linked and not treated as built | — | 10m | grapheon-tracera-absorption spec.md | Current behavior is written down with the command or query used |
| AD-094 | Contract: the spec-only absorption package is linked and not treated as built | AD-093 | 10m | grapheon-tracera-absorption spec.md | Expected behavior is stated as a pass/fail check |
| AD-095 | Change: the spec-only absorption package is linked and not treated as built | AD-094 | 20m | grapheon-tracera-absorption spec.md | The surface matches the contract or the gap is recorded as still open |
| AD-096 | Prove: the spec-only absorption package is linked and not treated as built | AD-095 | 10m | grapheon-tracera-absorption spec.md | The check fails on the broken input and passes on the fixed input |
| AD-097 | Record: adoption does not flip the witness status | — | 10m | STATE.md DELIVERY_REPAIR_PRODUCT_WITNESS_OPEN | Current behavior is written down with the command or query used |
| AD-098 | Contract: adoption does not flip the witness status | AD-097 | 10m | STATE.md DELIVERY_REPAIR_PRODUCT_WITNESS_OPEN | Expected behavior is stated as a pass/fail check |
| AD-099 | Change: adoption does not flip the witness status | AD-098 | 20m | STATE.md DELIVERY_REPAIR_PRODUCT_WITNESS_OPEN | The surface matches the contract or the gap is recorded as still open |
| AD-100 | Prove: adoption does not flip the witness status | AD-099 | 10m | STATE.md DELIVERY_REPAIR_PRODUCT_WITNESS_OPEN | The check fails on the broken input and passes on the fixed input |

