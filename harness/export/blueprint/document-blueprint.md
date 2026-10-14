# Whitepaper blueprint

The whitepaper is the dossier made *readable* — for someone who will sit down with it.

## Shape

Three template sections (`assets/templates/vantage-whitepaper.docx`):

| Section | Content | Furniture |
|---|---|---|
| 0 | cover (client logo, image, title, as-of, confidence/EQI, verification, marking), then Document control · Read before use · About · Handling | marking in the footer |
| 1 | table of contents | "Contents" header |
| 2 | the body | running title; marking + `Page N` |

The plan controls only what goes into the body, plus the abstract and the appendix selection.

## Length

| Depth | Body treatment | Appendices (`§21` subsections) |
|---|---|---|
| `exec` | §1 verbatim, the rest as summaries (verdict + lead paragraph) | 21.11 |
| `standard` | §1 verbatim, §0 and §2–§20 condensed | 21.1, 21.8, 21.11 |
| `full` | everything verbatim, §21 whole | — (§21 is in the body) |

## Treatments

| `treatment` | Effect |
|---|---|
| `verbatim` | the dossier's content passes through unchanged |
| `condense` | tables, callouts, charts, figures and lists kept; prose trimmed to two paragraphs per section — never a paragraph carrying an integrity marker |
| `summary` | the section is replaced by your `summary` text (which must carry its claim references) |
| `omit` | dropped entirely — almost never right |

## Section numbering

The document keeps the **dossier's own numbers** (§0–§21). Word's automatic numbering is disabled
because renumbering breaks every cross-reference ("see §6.4"). Never supply a `heading_override`
that changes a number. Inline `§x.y` and `[S-nnnn]` references become internal links where the
target is in the document.

## Elements the renderer provides

- **Callouts** — verdict (accent), warning/erratum (amber), disclaimer (grey italic), note.
- **Lead** — one italic line under each top-level heading. Write these for this client.
- **Charts and figures** — rendered where the dossier placed them, captioned with id and sources.
- **Abstract** — a callout on the front-matter page, 400–700 characters: the verdict and its
  single biggest caveat.

## Contents page

Built in two passes when a PDF is requested: render → PDF → read back printed page numbers →
re-render. A `docx`-only export leaves a TOC field for Word to populate.
