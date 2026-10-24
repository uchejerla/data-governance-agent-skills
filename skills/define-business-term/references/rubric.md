# Term definition rubric

Score the draft before it leaves your hands. Severity decides the verdict; the numeric
score is only for tracking quality over time and **must never override a blocker**.

Report the score as `criteria met / 20`, and state the verdict separately.

## Verdict

| Verdict | Condition |
| --- | --- |
| **Ready for review** | 0 blockers, 0 major |
| **Needs work** | 0 blockers, 1–2 major |
| **Not publishable** | any blocker |

"Ready for review" means ready for a human approver, not ready to publish.

---

## Blockers — any one of these and it does not go to review

| # | Criterion | Fails when | Why it matters |
| --- | --- | --- | --- |
| B1 | **Evidence-grounded** | A substantive claim has no source and is not marked `OPEN` | An invented definition is worse than no definition: it gets adopted, then trusted |
| B2 | **Not circular** | The term, or its synonym, appears in its own definition; or A is defined via B and B via A | Circularity feels complete while conveying nothing, so it survives review unnoticed |
| B3 | **Scope stated** | Enterprise / business unit / legal entity / region / product is unstated | The same word legally means different things across entities; unstated scope guarantees a dispute |
| B4 | **Threshold declared** | "Active", "current", "recent", "complete", "material", "valid" is used without a threshold, and it is not `OPEN` | Undeclared thresholds are the single largest source of metric reconciliation failures |
| B5 | **Ownership named** | No steward, SME or approver (or `OPEN` with a named person to ask) | An orphan term has no one to arbitrate it later |
| B6 | **Duplicate check recorded** | No search performed, or performed without recording where and what was found | A near-duplicate creates two competing truths, which is the exact failure the glossary exists to prevent |
| B7 | **Implementation-independent** | Definition names a table, column, report, vendor tool or SQL | The definition dies at the next migration and takes its authority with it |

## Major — fix before review where possible

| # | Criterion | Fails when |
| --- | --- | --- |
| M1 | **Boundary statement** | No explicit in-scope / out-of-scope, or exclusions without a "use X instead" pointer |
| M2 | **Examples** | Fewer than 2 positive or no negative example |
| M3 | **Neighbour disambiguation** | The 2 nearest terms are not contrasted, or the contrast is a restatement |
| M4 | **Atomic** | Two concepts in one entry, or a filter/grain/threshold baked into the term itself |
| M5 | **Concise** | Definition exceeds 3 sentences, or mixes meaning with calculation, process or history |
| M6 | **Plain language** | Jargon chains, undefined acronyms, or a definition harder than the term |
| M7 | **Sensitivity assessed** | No assessment of personal / financial / regulated data, or of jurisdiction dependency |

## Minor — note them, do not block

| # | Criterion |
| --- | --- |
| N1 | Obvious synonyms and abbreviations populated |
| N2 | Examples drawn from real records or real reports, not invented scenarios |
| N3 | Source evidence linked (document, policy clause, ticket) |
| N4 | Related and contrasting terms cross-linked |
| N5 | Naming convention followed (singular noun, sentence case, no trailing period in the label) |
| N6 | Calculation field present and non-empty where a calculation exists |

---

## Confidence

State one, based on the evidence you actually had:

- **High** — confirmed by a primary source or the accountable SME.
- **Medium** — consistent across two or more secondary sources, no SME confirmation.
- **Low** — inferred from usage or schema only. Say so; the approver needs to know what
  they are actually signing.

Confidence is not a quality score. A high-confidence entry can still fail a blocker.

## Reviewing someone else's entry

Work blockers first and stop there if any exist — listing twenty minor issues alongside
two blockers makes the two blockers look optional. Report at most: the blockers, then the
two or three changes that would most improve the entry, then the good decisions worth
keeping so they are not argued away in the next revision.
