---
object: "<schema.table or schema.table.column>"
object_type: dataset        # dataset | column | dataset+columns
status: draft               # draft | needs-owner-input | ready-for-review | deferred
verdict: needs-work         # ready-for-review | needs-work | not-publishable
coverage: "0 verified / 0 derived / 0 deferred"
domain: "<domain / subdomain>"
owner: "<name or OPEN>"
approver: "<name or OPEN>"
sensitivity: "<pointer to the classification of record, or OPEN>"
last_updated: "<YYYY-MM-DD>"
---

# Description proposal: <object>

> Fill every field. Replace unknowns with `OPEN` — never with plausible-sounding prose.
> Delete the guidance in each section before submitting for review.
> For a bulk request, copy this file per table. Never one file per column.

## Summary

<!-- One sentence: what this object is for, and its grain.
     Dataset: "One row per payment authorisation attempt, including declines and retries."
     Column: "Gross amount charged to the card, in minor units of the transaction currency." -->

## Grain and keys

<!-- Datasets only. Delete for a single column.
     The sentence the whole description depends on:
     "One row per <entity> per <event or period>, uniquely identified by <key>."
     Then state the table kind and what it means for counting. -->

- **One row:** <!-- entity / event / period -->
- **Key:** <!-- column(s), or "no uniqueness constraint" + what you found -->
- **Table kind:** <!-- event | snapshot | current-state | bridge -->
- **Counting consequence:** <!-- e.g. retries add rows; summing a snapshot double-counts -->

## Time and lifecycle

<!-- Event time vs processing time, timezone, snapshot vs incremental.
     How rows arrive, are corrected, are deleted (soft delete? restatement?). -->

## What it does not contain

<!-- The exclusions that cause wrong joins or wrong totals, and where that data lives instead.
     e.g. "Cancelled orders — see order_event. Sandbox attempts tagged environment='test'. -->"

## Freshness

- **Cadence:** <!-- streaming | hourly | nightly -->
- **Expected lag:** <!-- e.g. "under 60 seconds; settlement fields up to 24 hours" -->

## Columns

<!-- One row per column. The description column must stand alone — no "see above".
     Pattern: <meaning> · <unit/format> · <allowed values or derivation> · <null meaning> · <trap>
     Evidence: what you actually checked (DDL, constraint, full distinct, sample, doc, owner).
     Tier: A = verified · B = derived, review · C = deferred, owner required. -->

| Column | Proposed description | Evidence | Tier |
| --- | --- | --- | --- |
| | | | |

## Domain values

<!-- Enumerations you verified, with the source. Repeat per categorical column. -->

| Column | Values | Source of the list |
| --- | --- | --- |
| | | |

## Swap test

<!-- Pairs of near-neighbours whose descriptions were exchanged. If both still read as true,
     both are too vague. Record the pair and the verdict. -->

| Pair | Verdict |
| --- | --- |
| | |

## Caveats and known issues

<!-- Sentinel values, deprecated columns, historical changes, test data in a production table.
     Say the direction and size of the bias where you know it. -->

## Sensitivity and classification

<!-- A pointer, not a claim: where the classification of record lives, and which columns are
     candidates for review. Never write "contains no personal data". -->

## Open questions

<!-- Phrase as questions for a named person, not as hedged statements.
     e.g. "For MDM (R. Okafor): does is_active=false mean superseded, or churned?" -->

1.
2.

## Deferred

<!-- C — deferred objects only. A named owner per item; this is a deliverable, not a gap. -->

| Object | Why deferred | Owner to ask |
| --- | --- | --- |
| | | |

## Coverage

<!-- Verified / derived / deferred, with the total. Report these separately — never "described". -->

## Approval recommendation

<!-- Ready for review | Needs owner input | Deferred.
     One line of reasoning. Name the approver and the specific decision you are asking for. -->
