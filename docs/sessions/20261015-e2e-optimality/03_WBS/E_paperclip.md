# E. Paperclip: Daemon, Projects, Agents, Tools

**Phase:** P5 (Paperclip)  
**Task Prefix:** PC-001..PC-100  
**Goal:** Make Paperclip show Tracera, AgilePlus, and PhenoRegistry, with the local daemon, adapters, tools, and herdr state actually connected.  
**Depends On:** P4  
**Unlocks:** P6

Each surface is one real gap. The four leaves on a surface are record, contract, change, and proof. They are not index clones.

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|------------|-----|---------|------------|
| PC-001 | Record: the local daemon stop on 2026-10-14 | — | 10m | Paperclip daemon log, SIGTERM 2026-10-14 | Current behavior is written down with the command or query used |
| PC-002 | Contract: the local daemon stop on 2026-10-14 | PC-001 | 10m | Paperclip daemon log, SIGTERM 2026-10-14 | Expected behavior is stated as a pass/fail check |
| PC-003 | Change: the local daemon stop on 2026-10-14 | PC-002 | 20m | Paperclip daemon log, SIGTERM 2026-10-14 | The surface matches the contract or the gap is recorded as still open |
| PC-004 | Prove: the local daemon stop on 2026-10-14 | PC-003 | 10m | Paperclip daemon log, SIGTERM 2026-10-14 | The check fails on the broken input and passes on the fixed input |
| PC-005 | Record: how the local daemon is started without assuming systemd | — | 10m | Paperclip process supervisor on this Mac | Current behavior is written down with the command or query used |
| PC-006 | Contract: how the local daemon is started without assuming systemd | PC-005 | 10m | Paperclip process supervisor on this Mac | Expected behavior is stated as a pass/fail check |
| PC-007 | Change: how the local daemon is started without assuming systemd | PC-006 | 20m | Paperclip process supervisor on this Mac | The surface matches the contract or the gap is recorded as still open |
| PC-008 | Prove: how the local daemon is started without assuming systemd | PC-007 | 10m | Paperclip process supervisor on this Mac | The check fails on the broken input and passes on the fixed input |
| PC-009 | Record: the local Paperclip HTTP listener | — | 10m | localhost:3180 | Current behavior is written down with the command or query used |
| PC-010 | Contract: the local Paperclip HTTP listener | PC-009 | 10m | localhost:3180 | Expected behavior is stated as a pass/fail check |
| PC-011 | Change: the local Paperclip HTTP listener | PC-010 | 20m | localhost:3180 | The surface matches the contract or the gap is recorded as still open |
| PC-012 | Prove: the local Paperclip HTTP listener | PC-011 | 10m | localhost:3180 | The check fails on the broken input and passes on the fixed input |
| PC-013 | Record: the public endpoint that stayed up after the local stop | — | 10m | public Cloudflare-Access Paperclip endpoint | Current behavior is written down with the command or query used |
| PC-014 | Contract: the public endpoint that stayed up after the local stop | PC-013 | 10m | public Cloudflare-Access Paperclip endpoint | Expected behavior is stated as a pass/fail check |
| PC-015 | Change: the public endpoint that stayed up after the local stop | PC-014 | 20m | public Cloudflare-Access Paperclip endpoint | The surface matches the contract or the gap is recorded as still open |
| PC-016 | Prove: the public endpoint that stayed up after the local stop | PC-015 | 10m | public Cloudflare-Access Paperclip endpoint | The check fails on the broken input and passes on the fixed input |
| PC-017 | Record: the only project currently stored | — | 10m | Paperclip DB project Onboarding | Current behavior is written down with the command or query used |
| PC-018 | Contract: the only project currently stored | PC-017 | 10m | Paperclip DB project Onboarding | Expected behavior is stated as a pass/fail check |
| PC-019 | Change: the only project currently stored | PC-018 | 20m | Paperclip DB project Onboarding | The surface matches the contract or the gap is recorded as still open |
| PC-020 | Prove: the only project currently stored | PC-019 | 10m | Paperclip DB project Onboarding | The check fails on the broken input and passes on the fixed input |
| PC-021 | Record: the zero-goal count on Onboarding | PC-020 | 10m | Onboarding goals collection | Current behavior is written down with the command or query used |
| PC-022 | Contract: the zero-goal count on Onboarding | PC-021 | 10m | Onboarding goals collection | Expected behavior is stated as a pass/fail check |
| PC-023 | Change: the zero-goal count on Onboarding | PC-022 | 20m | Onboarding goals collection | The surface matches the contract or the gap is recorded as still open |
| PC-024 | Prove: the zero-goal count on Onboarding | PC-023 | 10m | Onboarding goals collection | The check fails on the broken input and passes on the fixed input |
| PC-025 | Record: the seven issues on Onboarding | — | 10m | Onboarding issues collection | Current behavior is written down with the command or query used |
| PC-026 | Contract: the seven issues on Onboarding | PC-025 | 10m | Onboarding issues collection | Expected behavior is stated as a pass/fail check |
| PC-027 | Change: the seven issues on Onboarding | PC-026 | 20m | Onboarding issues collection | The surface matches the contract or the gap is recorded as still open |
| PC-028 | Prove: the seven issues on Onboarding | PC-027 | 10m | Onboarding issues collection | The check fails on the broken input and passes on the fixed input |
| PC-029 | Record: a Tracera project row, with no sample goals | — | 10m | Paperclip project Tracera | Current behavior is written down with the command or query used |
| PC-030 | Contract: a Tracera project row, with no sample goals | PC-029 | 10m | Paperclip project Tracera | Expected behavior is stated as a pass/fail check |
| PC-031 | Change: a Tracera project row, with no sample goals | PC-030 | 20m | Paperclip project Tracera | The surface matches the contract or the gap is recorded as still open |
| PC-032 | Prove: a Tracera project row, with no sample goals | PC-031 | 10m | Paperclip project Tracera | The check fails on the broken input and passes on the fixed input |
| PC-033 | Record: an AgilePlus project row, with no sample goals | — | 10m | Paperclip project AgilePlus | Current behavior is written down with the command or query used |
| PC-034 | Contract: an AgilePlus project row, with no sample goals | PC-033 | 10m | Paperclip project AgilePlus | Expected behavior is stated as a pass/fail check |
| PC-035 | Change: an AgilePlus project row, with no sample goals | PC-034 | 20m | Paperclip project AgilePlus | The surface matches the contract or the gap is recorded as still open |
| PC-036 | Prove: an AgilePlus project row, with no sample goals | PC-035 | 10m | Paperclip project AgilePlus | The check fails on the broken input and passes on the fixed input |
| PC-037 | Record: a PhenoRegistry project row, with no sample goals | — | 10m | Paperclip project PhenoRegistry | Current behavior is written down with the command or query used |
| PC-038 | Contract: a PhenoRegistry project row, with no sample goals | PC-037 | 10m | Paperclip project PhenoRegistry | Expected behavior is stated as a pass/fail check |
| PC-039 | Change: a PhenoRegistry project row, with no sample goals | PC-038 | 20m | Paperclip project PhenoRegistry | The surface matches the contract or the gap is recorded as still open |
| PC-040 | Prove: a PhenoRegistry project row, with no sample goals | PC-039 | 10m | Paperclip project PhenoRegistry | The check fails on the broken input and passes on the fixed input |
| PC-041 | Record: Hermes has no AI provider | PC-040 | 10m | Hermes agent provider config | Current behavior is written down with the command or query used |
| PC-042 | Contract: Hermes has no AI provider | PC-041 | 10m | Hermes agent provider config | Expected behavior is stated as a pass/fail check |
| PC-043 | Change: Hermes has no AI provider | PC-042 | 20m | Hermes agent provider config | The surface matches the contract or the gap is recorded as still open |
| PC-044 | Prove: Hermes has no AI provider | PC-043 | 10m | Hermes agent provider config | The check fails on the broken input and passes on the fixed input |
| PC-045 | Record: the empty VP-Engineering adapter | — | 10m | VP-Engineering process adapter | Current behavior is written down with the command or query used |
| PC-046 | Contract: the empty VP-Engineering adapter | PC-045 | 10m | VP-Engineering process adapter | Expected behavior is stated as a pass/fail check |
| PC-047 | Change: the empty VP-Engineering adapter | PC-046 | 20m | VP-Engineering process adapter | The surface matches the contract or the gap is recorded as still open |
| PC-048 | Prove: the empty VP-Engineering adapter | PC-047 | 10m | VP-Engineering process adapter | The check fails on the broken input and passes on the fixed input |
| PC-049 | Record: the empty StaffSWE-Jcode adapter | — | 10m | StaffSWE-Jcode process adapter | Current behavior is written down with the command or query used |
| PC-050 | Contract: the empty StaffSWE-Jcode adapter | PC-049 | 10m | StaffSWE-Jcode process adapter | Expected behavior is stated as a pass/fail check |
| PC-051 | Change: the empty StaffSWE-Jcode adapter | PC-050 | 20m | StaffSWE-Jcode process adapter | The surface matches the contract or the gap is recorded as still open |
| PC-052 | Prove: the empty StaffSWE-Jcode adapter | PC-051 | 10m | StaffSWE-Jcode process adapter | The check fails on the broken input and passes on the fixed input |
| PC-053 | Record: whether StaffSWE-Codex has a process adapter | — | 10m | StaffSWE-Codex process adapter | Current behavior is written down with the command or query used |
| PC-054 | Contract: whether StaffSWE-Codex has a process adapter | PC-053 | 10m | StaffSWE-Codex process adapter | Expected behavior is stated as a pass/fail check |
| PC-055 | Change: whether StaffSWE-Codex has a process adapter | PC-054 | 20m | StaffSWE-Codex process adapter | The surface matches the contract or the gap is recorded as still open |
| PC-056 | Prove: whether StaffSWE-Codex has a process adapter | PC-055 | 10m | StaffSWE-Codex process adapter | The check fails on the broken input and passes on the fixed input |
| PC-057 | Record: whether StaffSWE-Kcode has a process adapter | — | 10m | StaffSWE-Kcode process adapter | Current behavior is written down with the command or query used |
| PC-058 | Contract: whether StaffSWE-Kcode has a process adapter | PC-057 | 10m | StaffSWE-Kcode process adapter | Expected behavior is stated as a pass/fail check |
| PC-059 | Change: whether StaffSWE-Kcode has a process adapter | PC-058 | 20m | StaffSWE-Kcode process adapter | The surface matches the contract or the gap is recorded as still open |
| PC-060 | Prove: whether StaffSWE-Kcode has a process adapter | PC-059 | 10m | StaffSWE-Kcode process adapter | The check fails on the broken input and passes on the fixed input |
| PC-061 | Record: whether StaffSWE-WinRemote has a process adapter | PC-060 | 10m | StaffSWE-WinRemote process adapter | Current behavior is written down with the command or query used |
| PC-062 | Contract: whether StaffSWE-WinRemote has a process adapter | PC-061 | 10m | StaffSWE-WinRemote process adapter | Expected behavior is stated as a pass/fail check |
| PC-063 | Change: whether StaffSWE-WinRemote has a process adapter | PC-062 | 20m | StaffSWE-WinRemote process adapter | The surface matches the contract or the gap is recorded as still open |
| PC-064 | Prove: whether StaffSWE-WinRemote has a process adapter | PC-063 | 10m | StaffSWE-WinRemote process adapter | The check fails on the broken input and passes on the fixed input |
| PC-065 | Record: Engineer-General reports to a StaffSWE | — | 10m | Engineer-General reportsTo | Current behavior is written down with the command or query used |
| PC-066 | Contract: Engineer-General reports to a StaffSWE | PC-065 | 10m | Engineer-General reportsTo | Expected behavior is stated as a pass/fail check |
| PC-067 | Change: Engineer-General reports to a StaffSWE | PC-066 | 20m | Engineer-General reportsTo | The surface matches the contract or the gap is recorded as still open |
| PC-068 | Prove: Engineer-General reports to a StaffSWE | PC-067 | 10m | Engineer-General reportsTo | The check fails on the broken input and passes on the fixed input |
| PC-069 | Record: Engineer-Specialist reports to a StaffSWE | — | 10m | Engineer-Specialist reportsTo | Current behavior is written down with the command or query used |
| PC-070 | Contract: Engineer-Specialist reports to a StaffSWE | PC-069 | 10m | Engineer-Specialist reportsTo | Expected behavior is stated as a pass/fail check |
| PC-071 | Change: Engineer-Specialist reports to a StaffSWE | PC-070 | 20m | Engineer-Specialist reportsTo | The surface matches the contract or the gap is recorded as still open |
| PC-072 | Prove: Engineer-Specialist reports to a StaffSWE | PC-071 | 10m | Engineer-Specialist reportsTo | The check fails on the broken input and passes on the fixed input |
| PC-073 | Record: the missing kind:personal field | — | 10m | Paperclip issue schema kind:personal | Current behavior is written down with the command or query used |
| PC-074 | Contract: the missing kind:personal field | PC-073 | 10m | Paperclip issue schema kind:personal | Expected behavior is stated as a pass/fail check |
| PC-075 | Change: the missing kind:personal field | PC-074 | 20m | Paperclip issue schema kind:personal | The surface matches the contract or the gap is recorded as still open |
| PC-076 | Prove: the missing kind:personal field | PC-075 | 10m | Paperclip issue schema kind:personal | The check fails on the broken input and passes on the fixed input |
| PC-077 | Record: herdr pane state does not arrive in Paperclip | — | 10m | herdr pane snapshot | Current behavior is written down with the command or query used |
| PC-078 | Contract: herdr pane state does not arrive in Paperclip | PC-077 | 10m | herdr pane snapshot | Expected behavior is stated as a pass/fail check |
| PC-079 | Change: herdr pane state does not arrive in Paperclip | PC-078 | 20m | herdr pane snapshot | The surface matches the contract or the gap is recorded as still open |
| PC-080 | Prove: herdr pane state does not arrive in Paperclip | PC-079 | 10m | herdr pane snapshot | The check fails on the broken input and passes on the fixed input |
| PC-081 | Record: the seven Paperclip tools, named from the Paperclip source before any MCP registration | PC-080 | 10m | Paperclip tool catalog | Current behavior is written down with the command or query used |
| PC-082 | Contract: the seven Paperclip tools, named from the Paperclip source before any MCP registration | PC-081 | 10m | Paperclip tool catalog | Expected behavior is stated as a pass/fail check |
| PC-083 | Change: the seven Paperclip tools, named from the Paperclip source before any MCP registration | PC-082 | 20m | Paperclip tool catalog | The surface matches the contract or the gap is recorded as still open |
| PC-084 | Prove: the seven Paperclip tools, named from the Paperclip source before any MCP registration | PC-083 | 10m | Paperclip tool catalog | The check fails on the broken input and passes on the fixed input |
| PC-085 | Record: those seven named tools are absent from tracera-mcp | — | 10m | tracera-mcp Paperclip tool registration | Current behavior is written down with the command or query used |
| PC-086 | Contract: those seven named tools are absent from tracera-mcp | PC-085 | 10m | tracera-mcp Paperclip tool registration | Expected behavior is stated as a pass/fail check |
| PC-087 | Change: those seven named tools are absent from tracera-mcp | PC-086 | 20m | tracera-mcp Paperclip tool registration | The surface matches the contract or the gap is recorded as still open |
| PC-088 | Prove: those seven named tools are absent from tracera-mcp | PC-087 | 10m | tracera-mcp Paperclip tool registration | The check fails on the broken input and passes on the fixed input |
| PC-089 | Record: phase 2 routes and UI are unbuilt | — | 10m | cockpit phase 2 | Current behavior is written down with the command or query used |
| PC-090 | Contract: phase 2 routes and UI are unbuilt | PC-089 | 10m | cockpit phase 2 | Expected behavior is stated as a pass/fail check |
| PC-091 | Change: phase 2 routes and UI are unbuilt | PC-090 | 20m | cockpit phase 2 | The surface matches the contract or the gap is recorded as still open |
| PC-092 | Prove: phase 2 routes and UI are unbuilt | PC-091 | 10m | cockpit phase 2 | The check fails on the broken input and passes on the fixed input |
| PC-093 | Record: phase 3 routes and UI are unbuilt | — | 10m | cockpit phase 3 | Current behavior is written down with the command or query used |
| PC-094 | Contract: phase 3 routes and UI are unbuilt | PC-093 | 10m | cockpit phase 3 | Expected behavior is stated as a pass/fail check |
| PC-095 | Change: phase 3 routes and UI are unbuilt | PC-094 | 20m | cockpit phase 3 | The surface matches the contract or the gap is recorded as still open |
| PC-096 | Prove: phase 3 routes and UI are unbuilt | PC-095 | 10m | cockpit phase 3 | The check fails on the broken input and passes on the fixed input |
| PC-097 | Record: live Paperclip agents versus the org chart, company id 80f9a008-58f8-46e1-ae2e-c06c3cd06c9b | — | 10m | phenotype-registry docs/org/org-chart.md | Current behavior is written down with the command or query used |
| PC-098 | Contract: live Paperclip agents versus the org chart, company id 80f9a008-58f8-46e1-ae2e-c06c3cd06c9b | PC-097 | 10m | phenotype-registry docs/org/org-chart.md | Expected behavior is stated as a pass/fail check |
| PC-099 | Change: live Paperclip agents versus the org chart, company id 80f9a008-58f8-46e1-ae2e-c06c3cd06c9b | PC-098 | 20m | phenotype-registry docs/org/org-chart.md | The surface matches the contract or the gap is recorded as still open |
| PC-100 | Prove: live Paperclip agents versus the org chart, company id 80f9a008-58f8-46e1-ae2e-c06c3cd06c9b | PC-099 | 10m | phenotype-registry docs/org/org-chart.md | The check fails on the broken input and passes on the fixed input |

