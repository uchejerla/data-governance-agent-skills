# Description rubric

Score before the description leaves your hands. Severity decides the verdict; the numeric
score tracks quality over time and **never overrides a blocker**.

Twenty criteria, but not all apply to every object: grain (B2), lifecycle (M4) and freshness
(M5) apply to a dataset, and a single column has nothing to say about them. Mark those
`N/A`, score `met / applicable`, and report the verdict separately.

## Verdict

| Verdict | Condition |
| --- | --- |
| **Ready for review** | 0 blockers, 0 major |
| **Needs work** | 0 blockers, 1–2 major |
| **Not publishable** | any blocker |

"Ready for review" means ready for the object's owner, not ready to publish. A description
that passes every criterion is still only as good as its evidence tier.

---

## Blockers — any one of these and it does not go to review

| # | Criterion | Fails when | Why it matters |
| --- | --- | --- | --- |
| B1 | **Evidence tiered** | A description has no evidence and is not marked `inferred`; or `inferred` text is presented as verified | A plausible guess is adopted and trusted; a labelled one gets checked |
| B2 | **Grain and key stated** | A dataset description never says what one row is, or claims uniqueness without naming the key | Every count, join and aggregate downstream depends on this one sentence |
| B3 | **Adds information** | The description restates the object name, the data type, or both ("`status` — the status of the record") | A caption consumes the reader's attention and returns nothing; it also teaches an agent that the column is unremarkable |
| B4 | **Units and formats stated** | Money without currency or minor-unit convention; timestamps without timezone; durations, percentages or rates without a defined denominator | An agent will sum pence as pounds and answer confidently; the error is silent and 100× |
| B5 | **Domain bounded** | A categorical column is described as "status", "type" or "category" without its values, or without `OPEN` and an owner | Undocumented enums are guessed, and the wrong branch is chosen without an error |
| B6 | **Null semantics stated** | `NULL` is possible and its meaning (unknown / not applicable / not yet evaluated / not permitted) is unstated, where interpretation depends on it | `NULL` is read as zero, as false, or as a gap in the data — three different answers from one value |
| B7 | **No unverified absence or classification claim** | "Contains no personal data", "always populated", "never null", "no free text", or a sensitivity label asserted from the column name | Absence claims are never re-checked, and a wrong classification is a regulatory exposure rather than a documentation defect |

## Major — fix before review where possible

| # | Criterion | Fails when |
| --- | --- | --- |
| M1 | **Meaning, not pipeline** | The description explains the job, the schedule, the storage format or the source table instead of what the value means; or it names a build artifact where a semantic statement would do |
| M2 | **Derivation explained** | A derived column does not say what it is derived from, or copies a formula that is maintained elsewhere instead of pointing to it |
| M3 | **Disambiguated** | The nearest confusable object is not separated, or the swap test leaves both descriptions true |
| M4 | **Time and lifecycle** | Event time vs processing time is unstated; snapshot vs incremental is unstated; soft deletes, restatements or superseded rows are not mentioned |
| M5 | **Freshness stated** | No update cadence or expected lag, so a consumer cannot tell how stale an answer is |
| M6 | **Classification pointer** | A sensitive-looking column carries no pointer to its classification of record and no candidate flag |
| M7 | **Concise and standalone** | Summary longer than one sentence, a column description longer than two, pasted wiki prose, or a description that only makes sense after reading another object's |

## Minor — note them, do not block

| # | Criterion |
| --- | --- |
| N1 | Consistent voice and tense across the object — describes the value in the present tense, no "we", no "this field is used to" |
| N2 | Example values drawn from real data, not invented |
| N3 | Related objects and their keys cross-linked |
| N4 | Owner or contact recorded |
| N5 | Domain and tags aligned with the taxonomy, not invented locally |
| N6 | No references that will rot — no wiki pages, ticket IDs or job names where a semantic statement would do |

---

## Evidence tiers

The tier is the confidence measure for this skill. State it per object; do not average it
across a table.

| Tier | Basis | Publishable |
| --- | --- | --- |
| **A — verified** | `observed` from constraints or full-domain checks, or `documented`, or `asserted` by the owner | Yes, after owner review |
| **B — derived** | Consistent evidence from schema, sampling and lineage, with no confirmation | No — review queue |
| **C — deferred** | Meaning cannot be established from available evidence | No — named owner required |

An `inferred` description is a hypothesis at tier B at best. Ten consistent guesses do not
add up to a verified table, and the batch tier is the **lowest** tier in it, never the
average.

## Reviewing someone else's descriptions

Work blockers first and stop there if any exist — listing twenty minor issues beside two
blockers makes the blockers look optional. Then report, at most:

1. the blockers, with the specific fix for each;
2. the two or three changes that would most improve the object, usually grain and units;
3. the good decisions worth keeping, so they survive the next revision.

For a bulk submission, review per table: state the grain, the tier counts, the swap-test
pairs, and the deferred list. Do not walk a reviewer through forty sentences one at a time —
that is how review becomes rubber-stamping.
