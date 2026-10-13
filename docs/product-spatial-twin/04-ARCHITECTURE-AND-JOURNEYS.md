# Architecture, journeys and behavioral contract

**Status:** proposed; not a declaration of implemented services.

## Hexagonal composition

~~~text
Canonical Tracera product + typed evidence graph (existing model authority)
             |
      scoped query/read port
             |
 projection compiler (schema/permissions/temporal context, agnostic to renderer)
             |
  semantic scene IR + reversible identity index + completeness/provenance
             |
     presentation adapters / interaction controllers
        |             |                |
     Web 3D        2D/matrix     accessible tree/list
             |
  optional proposed change --> governance approval --> AgilePlus/external execution
~~~

Do not add a second repository-scoped graph DB or product registry to implement this diagram. Renderer choice and cache architecture remain experiments. Asset authoring belongs to presentation/domain asset systems.

## Journey J-01: software-only feature investigation

**Given:** product baseline and user capability with known source/requirement evidence; **when:** operator opens outer assembly, selects capability control, disassembles service cluster, follows a typed edge and inspection link; **then:** all views resolve the same canonical refs, expose provenance and a reversible breadcrumb. **Failure oracle:** decorative adjacency cannot be mistaken for a real `depends_on` edge.

## Journey J-02: failure/dissatisfaction diagnosis

**Given:** known failed acceptance criterion, observation and source link; **when:** operator activates runtime/verification lenses and traces source; **then:** show causal hypotheses *as hypotheses*, actual observation with timestamps, and failed/missing test evidence. **Failure oracle:** an unavailable telemetry source does not render as passing; assertions about causality require separate proof.

## Journey J-03: baseline/time travel

**Given:** two model revisions/configurations; **when:** operator compares exploded assemblies; **then:** changed/removed/added entities and their status are traceable without losing stable product identity. **Failure oracle:** historical deployment observation never shows up as present-tense verified behavior.

## Journey J-04: hardware/software hybrid

**Given:** CAD model with units/license and controlling software in the product graph; **when:** operator expands a mechanical actuator; **then:** real physical geometry is marked physical while software control modules are marked semantic; source CAD/firmware links resolve independently. **Failure oracle:** false mechanical scale cannot be inferred from metaphorical geometry.

## Journey J-05: massive cross-product topology

**Given:** dense typed graph; **when:** viewport node/edge budget is exceeded; **then:** aggregate membership and omissions are explicit, paths can be queried, and matrix/table alternatives remain usable. **Failure oracle:** no claim of full graph visibility or source completeness from a sampled projection.

## Journey J-06: editing / external agent workflow

**Given:** actor selects a hypothetical replacement; **when:** drag/drop or connector operation is requested; **then:** view enters proposal preview, computes affected canonical refs and demands separate authorization/gated work through existing execution governance. **Failure oracle:** no side effect on live product, code or deployment without authorized explicit action.

## Nonfunctional quality overlays

Readability, latency/interaction response, color-independent status, WCAG 2.2 AA-aligned keyboard/screen-reader paths, power/GPU budgets, permission isolation, time consistency, cache invalidation and scene-asset security are independent gates; no aesthetic polish compensates for a failed truth/authority condition. Define measured thresholds against actual targets after device/environment sampling.
