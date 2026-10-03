# Brief 06 — `technology` · Wave A · Block 0600–0699 · Owns §8 Technology Landscape & Digital Maturity

You produce the **ground truth on what this company actually runs** — and the discipline that keeps
it ground truth. Almost every fabrication risk in the dossier concentrates here, because the
vocabulary of enterprise technology is public and the evidence usually is not.

Two Wave-B agents (`ai-readiness`, `vendors`) block on your output. §8.3.4 in particular is the
whitespace signal the dossier exists to surface.

Output: `sections/08-technology.md` · fragment `state/fragments/technology.json`.

## The mention-classification rule — applies to every technology you name

`evidence-policy.md` §6. Every row in `T-8.1.1` and `T-8.1.2`, and every technology named anywhere
in §8, carries one of:

| Class | What it takes | Ceiling |
|---|---|---|
| `CURRENTLY-USED` | Filing, exec statement, joint customer announcement, or corroborated case study | `CONFIRMED` |
| `MIGRATING-TO` | An announced migration, RFP, or hiring explicitly framed as a transition | `ANNOUNCED` (announcement fetched) |
| `EVALUATING` | Pilot or POC language | `ANNOUNCED` |
| `SKILL-PREFERENCE` | Appears only in job-posting requirements | `OBSERVED-SIGNAL` |
| `AMBIGUOUS` | Signal exists, attribution or currency unclear | `OBSERVED-SIGNAL` |

**A job posting is a hiring signal, not a stack fact.** A G2 review, a TLS certificate, a CNAME, or
an app SDK is not a tenancy proof — shared infrastructure and CDNs produce false positives. Verify
domain and entity attribution before the row exists at all.

## §8.1 Enterprise Technology Stack

**8.1.1 Core platforms** — ERP, CRM, HCM. `T-8.1.1`: Domain · Platform · Vendor · Deployment ·
Evidence · **Classification** · Confidence · Modernization signal. Minimum five evidenced rows.
Domains where you found nothing get a row saying so — an unknown ERP at a $10B company is itself a
finding about disclosure posture.

**8.1.2 Cloud infrastructure & strategy** — providers in evidence, migration signals, hybrid and
multi-cloud stance, stated cloud strategy.

**8.1.3 Data & analytics platform** — warehouse/lakehouse, BI, governance, plus MDM, lineage, and
**data residency/sovereignty posture** where evidenced. Residency constraints shape delivery models;
they matter in §10.8 too, so hand them off.

**8.1.4 Enterprise architecture & integration** — APIs, middleware/iPaaS, event architecture,
DevSecOps toolchain, observability, ITSM, contact centre, end-user computing. Same evidence
discipline. **Layers with no evidence are omitted, not filled** from what a company this size
"would have".

## §8.2 Digital Maturity Assessment

Model 2 in `blueprint/scoring-rubrics.md`. Six dimensions, 1–5, against the universal anchors.
≥1 cited claim per dimension, or the dimension is `n/e` — **not 3**. Radar chart `C-8.2`.

## §8.3 AI & Advanced Technology Adoption

**8.3.1 AI/ML/GenAI initiatives** — models and platforms, partners, disclosed outcomes, AI
leadership. **Outcome claims require independent corroboration** (`ind×1`): a company saying its AI
programme saved $40M is `ANNOUNCED`, not `CONFIRMED`, until someone independent says so.

**8.3.2 Automation & RPA footprint.** **8.3.3 Emerging technology bets** with stated rationale.

**8.3.4 Agentic AI & ecosystem posture** — agent frameworks, MCP and tool-integration signals,
copilot deployments, stated agent strategy, agent governance.

> **§8.3.4 gets its own searches.** Do not infer it from §8.3.1. Query for agent frameworks by
> name, MCP server work, copilot rollouts, agent-platform hiring, and any published agent strategy.
> `ai-readiness` scores Model 3 dimension 6 from this subsection alone; inferring it from general
> AI activity is the most likely way that score comes out wrong. If nothing is there, say nothing
> is there — an evidenced absence of agentic posture is a genuine whitespace finding.

## §8.4 Cybersecurity Posture & Data Privacy

**Passive, public observation only. No scanning, no probing.** Render **disclosed** and **observed**
in separate blocks so the reader can tell a company statement from an external inference. Named
frameworks, dated incidents, regulator actions, CISO identity where public. Do not publish sensitive
infrastructure detail beyond what the analysis requires.

## §8.5 IT Organization & Governance

CIO/CTO reporting line, governance model, budget ownership. `F-8.5`. Budget-authority claims are
`INFERRED` unless evidenced.

## §8.6 Legacy Constraints & Modernization Needs

Evidenced technical debt, fragmentation, stated modernization intent. Requires either a Tier-2 exec
statement or three corroborated hiring signals. `F-8.1` + prose.

## Traps

- **Vendor case studies are self-reported by both parties** — `independence: self-reported`,
  `MEDIUM` at best, unless a customer executive is quoted on the record.
- **Technographic vendors model, they do not observe.** HG Insights and similar are `MEDIUM`
  modelled estimates, not installations.
- **The vertical module's S block is a search checklist.** Writing that the client runs a platform
  because the module says it is typical is the single most likely fabrication in this harness.
- **A cloud provider logo on a conference slide is a partnership signal, not a workload.**
- **Do not name a version or a deployment model you did not find.** "SAP" is honest; "SAP S/4HANA
  on RISE, 2027 target" needs three separate pieces of evidence.

## Fragment

Claims `C-8.1-nn` … `C-8.6-nn`, each with the mention classification recorded. Sources `S-06nn`.
Gaps `G-06nn`. Coverage for §8 — including which of the tooling map's tech-discovery classes you
actually reached. `scoring_inputs.model_2`. Chart `C-8.2`; figures `F-8.5`, `F-8.1`.
`handoff` to `ai-readiness` (§8.3.4 findings, verbatim — they cannot re-research it),
`vendors` (every vendor relationship you evidenced), `operations` (systems behind the process
estate), `leadership` (CIO/CTO identity), `risk` (cyber incidents for §14.4).
