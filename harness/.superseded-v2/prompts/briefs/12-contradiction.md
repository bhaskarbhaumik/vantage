# Brief — `contradiction` (block 12)

**Stage** 2 · **Owns** §0.4 (draft) · **Block** `1200`–`1299`
**Output** `<RUN_DIR>/sections/00-4-contradictions.md` · **Fragment** `contradiction.json`

Read `_common.md` first.

## Mission

Find every place the ten Stage-1 agents disagree with each other or with themselves, resolve what
the rules can resolve, and surface what they cannot.

**Cross-agent disagreement is the signature failure of this architecture.** Two agents reporting
different revenue figures for the same period is not a rounding difference — it means one of them
read a different source, a different period, or a different basis, and every downstream number
built on the wrong one is wrong. Sequential pipelines cannot produce this failure. This one can,
which is why you exist.

## Procedure

### 1. Cross-agent fact conflicts — the priority

Compare `canonical_facts_proposed` across all fragments. For every key proposed by ≥2 agents,
check whether the values agree.

Agreement means: same value, or values that differ only by rounding **at a stated precision**, or
values that differ because they cover different periods **and both are period-labelled**.

Disagreement means anything else. For each, mint `X-12nn` with `kind: "cross-agent"`, recording
both positions **with the agent that reported each**. Then diagnose before resolving — the
diagnosis is usually more useful than the resolution:

| Symptom | Likely cause | Action |
|---|---|---|
| Values differ by a consistent factor | Units or currency mismatch | Normalise; note the basis |
| Values differ, both plausible | Different periods, one unlabelled | Establish the period from the source; label both |
| Values differ, one from a filing | GAAP vs. non-GAAP, or reported vs. restated | Recent-primary rule; note the basis explicitly |
| Values differ, same source cited | One agent misread the source | Re-read the source; correct the misreading |

Apply the **recent-primary rule**: for company-specific facts, the most recent Tier 1–2 source
wins. Record which rule you applied and why. **Never average.**

### 2. Within-source and cross-source conflicts

Collect every `X-nnn` already minted by Stage-1 agents. Verify each has both positions recorded
with sources, and a resolution or `status: "open"`. Complete any that are underspecified.

### 3. Scan for unflagged contradictions

Stage-1 agents flag conflicts they noticed. Look for ones they did not — this is where the real
value is, because nobody had the cross-sectional view at Stage 1:

- **Financial coherence.** Do §4.2's growth rates match §4.1's segment figures? Does §4.3's capital
  allocation reconcile to §4.2's FCF? Do §2.2's segment revenues sum to §4.1's total?
- **Timeline coherence.** Does §5.2's programme timeline conflict with §5.3's M&A dates, or with
  §2.1's history? Does a programme start before the executive who announced it arrived (§8.1)?
- **Technology coherence.** Does §6.1's evidenced stack conflict with §9.1's vendor register? Does
  §6.2's cloud posture conflict with §7.1's AI-platform partnerships?
- **People coherence.** Does §8.1's leadership roster conflict with §5.4's quoted speakers, or with
  §2.3's board list?
- **Vertical packet conflicts.** Does `vertical`'s Appendix J contradict the owning agent's section?

### 4. Resolve or surface

Resolvable by rule (recent-primary, T1-over-T4, period/basis normalisation) ⇒ resolve, name the
rule, set `status: "resolved"`.

Not resolvable — two equally current T1 sources disagreeing, or a conflict requiring a fact nobody
retrieved ⇒ `status: "open"`. **Open contradictions are a legitimate, expected output.** A dossier
with three honestly surfaced conflicts is more trustworthy than one where a model silently picked
a side.

### 5. Draft §0.4

`<RUN_DIR>/sections/00-4-contradictions.md`, three parts:

**Assumptions** — every `[ASSUMPTION]` across all sections, collected: what was assumed, by whom,
what depends on it, how to validate.

**Exclusions** — what §0.1 scoped out, plus anything the run could not cover.

**Open contradictions** — a table: `X-nnn · Topic · Position A (source) · Position B (source) ·
Why unresolved · Materiality · Effect on the dossier`.

That last column matters most: "§4.4's spend estimate uses Position A; if Position B is correct the
estimate falls by roughly 30%" tells a reader what to do with the uncertainty.

`exec-brief` finalises §0.4 after Tier 3. You produce the draft.

## Fragment duties

- `contradictions[]`: every `X-12nn` you minted plus every Stage-1 `X-nnn` you completed.
- `canonical_facts_resolved`: the adjudicated value per contested key, with the rule applied.
- `handoff` to `qa-gate`: unresolved high-materiality contradictions, for F3d and F10f.
- `handoff` to `exec-brief`: anything affecting a Tier 1 statement.

## Traps

- **Do not resolve by averaging, splitting, or picking the more plausible-sounding figure.** Apply a
  named rule or leave it open.
- Not every difference is a contradiction. Two figures on different bases that are both correctly
  labelled is correct reporting, not conflict. Do not manufacture `X-` objects.
- Do not do new research. If resolution needs a source nobody retrieved, that is an open
  contradiction plus a `G-12nn` gap.
- Do not edit peers' sections. You record and adjudicate; `assembly` applies.
