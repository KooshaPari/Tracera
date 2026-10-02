# Lifecycle / PLM / SDLC design-debt register

**Status:** blocking research/design debt.
**Captured:** 2026-09-29.

## Why this exists

Tracera originated independently from a first-principles question: "can a product be decomposed/represented as a graph?" It was driven primarily by problems encountered while building software products, not by an attempt to reproduce PLM, ALM, requirements-engineering, or systems-engineering products.

That independence is useful for avoiding inherited assumptions, but it creates a material risk: Tracera may have rediscovered only selected pieces of decades of lifecycle/configuration/product-data practice while leaving important semantics underdeveloped.

Therefore existing industries are **design libraries to mine**, not merely competitors.

## Blocking knowledge domains to mine

### PLM / digital thread / product data
Investigate transferable semantics for:
- product structures and multiple BOM views;
- revisions vs versions;
- effectivity;
- variants/configurations/options;
- released vs working structures;
- change objects and engineering change orders;
- as-designed / as-built / as-maintained state;
- document/product-data management;
- supplier/external component relations;
- provenance and digital thread;
- lifecycle maturity/release states;
- baselines and configuration items.

### ALM / requirements / systems engineering
Investigate:
- requirements decomposition and allocation;
- suspect links;
- trace matrices;
- verification/validation;
- test management;
- configuration/baseline management;
- change impact;
- reviews/approvals/signatures;
- reuse/variants;
- safety/risk/hazard linkage;
- regulated evidence packages.

### SDLC / configuration and release management
Investigate:
- idea/discovery/design/build/test/release/deploy/operate/retire semantics;
- branch/release/version/channel relationships;
- environment and deployment identity;
- incident/problem/change feedback;
- deprecation and end-of-life;
- compatibility and migration;
- feature flags and progressive delivery;
- rollback/recovery;
- support/LTS;
- observability-to-product feedback.

### MBSE / SysML / architecture
Investigate:
- requirement/behavior/structure/constraint views;
- allocations;
- interfaces/ports/flows;
- viewpoints;
- parametrics;
- model libraries/reuse;
- verification cases;
- model/configuration management.

## Questions for every imported concept

1. Is this a universal product concept, a physical-product-specific concept, or a regulated-process artifact?
2. Does software already have a better native analogue?
3. Does Tracera need to own it, reference it, or derive it?
4. Can an existing standard/schema/API represent it?
5. Does it belong in canonical product truth, observed state, work/execution state, or evidence?
6. Can agents maintain it economically from observable artifacts?
7. What failure occurs if Tracera omits it?
8. Does adding it improve ordinary consumer/software development, or merely reproduce enterprise ceremony?

## Architecture constraint

Do not transplant PLM/ALM ceremony wholesale. Import semantics and invariants when they buy product truth, lifecycle reasoning, change safety, reuse, or verification. Keep processes adaptive and machine-maintainable.

## Expected output

The SOTA pass must produce:
- concept inventory;
- concept mapping into Tracera ontology;
- accepted/rejected/adapted decisions;
- lifecycle state model;
- configuration/version/variant model;
- change/delta model;
- release/deployment/operation/retirement model;
- requirements amendments;
- standards/interchange recommendations;
- pilot cases that test whether imported lifecycle semantics add value outside regulated engineering.
