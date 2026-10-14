# Classification, disclaimers and integrity — non-negotiable

Every collateral `vantage export` produces carries the configured classification marking
(`export.classification`, default **Confidential**). It is not a plan field and not an agent's
judgement call: the renderers stamp it.

A Vantage dossier contains outside-in assessments of a named company, scored attractiveness and
readiness models, named individuals as buying-centre targets and positioning against named
incumbents. A deck that escaped without its marking would be a live commercial incident.

## Where the marking appears

| Collateral | Placement | Enforced in |
|---|---|---|
| `.pptx` | bottom-left of **every** slide; closing card; `category` + `comments` properties | `pptx_render._chrome`, `._set_core_properties` |
| `.docx` | footer of every page (template placeholder), cover, Document control, Handling | `assets/templates/vantage-whitepaper.docx`, `docx_render` |
| `.pdf` | inherited from the `.docx` | — |
| HTML deck | every slide footer, the HUD, `<title>`, `classification` meta tag | `html_render._slide`, `._page` |
| microsite | fixed marking bar on every screen, nav footer, page footer, `<title>`, meta tag, print footer | `html_render`, `site.css` |
| all | `manifest.json` beside the artifacts | `api._write_manifest` |

## Reliability travels with the collateral

The cover of every collateral carries the dossier's **Overall Confidence (EQI)** and its
**verification result** (with blocker/major/minor counts). The deck adds a "How far this dossier
can be trusted" slide and a "Verification and disclosures" slide; the whitepaper's Document
control table and the microsite banner carry the same. The dossier's "Read before use" banner is
reproduced, never dropped.

## The scoring disclaimer

Wherever a score appears this sentence travels with it, verbatim, in the same view:

> Scores are evidence-based internal decision aids derived from outside-in public evidence. They
> are not measurements of the client and must not be presented to the client.

In a plan, put it in the slide's `notes` or the chart's `note`: the renderer then prints it on the
face of the slide.

## Suppressed scores

A composite the dossier marks **SUPPRESSED** reports no number. No collateral may print one — not
from an earlier draft, not reconstructed from the dimensions, not "roughly", not as a midpoint of
the sensitivity bounds. Show the band as withheld and say why.

## Markers

`[DATA GAP]`, `[DATA UNAVAILABLE]`, `[ESTIMATE]`/`[ESTIMATED]`, `[INFERRED]`, `[SNIPPET-ONLY]`,
`[STALE …]`, `[INTERNAL REQUIRED]`, `[INTERNAL: …]` and `NOT ASSESSED` stay attached to the
claim they qualify. The renderers re-append a marker that a display trim would cut, and the
whitepaper's `condense` treatment never drops a paragraph that carries one. A plan must not
paraphrase a marker away.

## Sharing

Never publish an export to a public URL. If a share link is wanted, it must be access-controlled
and the user must ask for it explicitly. The HTML is a single offline file precisely so it can be
shared through the same channels as the `.pptx`.
