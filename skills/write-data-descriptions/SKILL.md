---
name: write-data-descriptions
description: Use when someone asks to write, review, or bulk-fill the description of a table, dataset, or column — for example "describe this table", "why does the AI assistant pick the wrong column", "backfill descriptions for the finance schema", or "is this column description good enough". Produces a per-object description proposal covering grain, units, allowed values, null semantics, caveats and machine-readability, with evidence and confidence per object. Not for business term definitions or metric formulas — use define-business-term for those.
version: 0.1.0
last-reviewed: 2026-10-24
---

# Describe data so a person and a machine both use it correctly

A description is not a caption. It is the metadata someone — or something — reads to decide
whether this column answers their question. `status = "The status of the record"` is a
caption: it adds no information the column name did not already carry, and it leaves the unit,
the allowed values, the meaning of `NULL` and the trap all unstated.

A description answers three questions, in this order:

1. **What is this?** Business meaning, not the physical type.
2. **How do I read a value?** Unit, currency, format, allowed values, what `NULL` means.
3. **When should I not use it?** The gotcha, the exclusion, the neighbour it gets confused with.

For a dataset, answer one more first: **what is one row?**

**Produce:** a completed proposal from `assets/description-proposal.md`, plus a short summary
in chat. For a bulk request, one proposal per table with an honest coverage count.

## Why the bar moved

Descriptions now have a second reader: an agent generating SQL, which does not browse, does not
ask a follow-up, and does not notice a placeholder. It retrieves **per object**, so a column
description must stand alone, and it will merge two similarly described columns without saying
so. That makes confidently wrong descriptions worse than missing ones — a blank field prompts a
question, a plausible sentence gets adopted.

## When to use this

| Request | Action |
| --- | --- |
| Describe a table, dataset, view or materialised model | This skill |
| Describe one column, or a family of related columns | This skill |
| Review or improve existing descriptions | This skill, starting at step 7 |
| Backfill descriptions across a schema | This skill, bulk mode |
| "What does this column mean?" and the catalog already answers it | Answer the question; do not build a proposal |
| Define a business concept, or two teams disagree on a term | Hand off to `define-business-term` |
| A number with a formula, grain or window | It is a metric. Hand off to the metric skill |
| "Is this column personal data?" | Hand off to `classify-sensitive-data` — this skill flags candidates, it does not classify |
| Rename tables, redesign keys, fix a model | Out of scope. Describe what exists, and raise the design problem separately |

## Non-negotiables

1. **Every description carries its evidence, and `inferred` is a label, not a default.** The
   four tiers are `observed` (schema, constraints, sampled values), `documented` (an existing
   authoritative doc), `asserted` (an owner or engineer said so), and `inferred` (from the
   name or a pattern). Inferred is written down and routed to review; it is never published
   as though it were verified.
2. **Grain before columns.** If you cannot say what one row represents, say so and stop.
   Writing 40 column descriptions around a table whose grain you do not know produces 40
   plausible sentences and one unusable table.
3. **Restating is not describing.** `customer_id` → "The ID of the customer" spends the
   reader's attention and returns nothing. Every sentence has to add information that the
   object name and data type did not already contain.
4. **Units, currency, timezone and null meaning are part of the meaning.** This is the
   deliberate opposite of a glossary definition, which must survive a migration. A
   description is attached to a physical object, so physical facts belong in it — stated as
   facts (`amount_minor`, GBP pence), never as pipeline instructions (job names, schedules,
   storage formats).
5. **Never claim an absence or a classification you did not verify.** "Contains no personal
   data" and "always populated" are the two most dangerous sentences in a catalog, because
   nobody re-checks them. Flag candidates for classification; point at the record of
   authority rather than competing with it.
6. **Bulk is a batching strategy, not an approval.** Inferred descriptions go to review. The
   coverage number you report is the verified one, with derived and deferred counted
   separately.

## Procedure

### 1. Frame the object and the reader

Identify whether the target is a dataset, a column, or a table plus its columns, and who is
asking: an analyst browsing, an engineer joining, or an agent answering questions in natural
language. The reader tells you which fields carry the weight — ambiguous units for an agent,
keys and derivation for an engineer.

Capture what prompted the request, too: "the assistant keeps summing `amount` across
currencies" is a far better brief than "describe the payments table".

### 2. Establish grain and keys (datasets)

Write the sentence before anything else:

> One row per **⟨entity⟩** per **⟨event or period⟩**, uniquely identified by **⟨key⟩**.

Then record what kind of table it is, because it changes how every count should be read:

- **Event** — one row per business event. Retries and corrections create extra rows.
- **Snapshot** — one row per entity per period. Summing across periods double-counts.
- **Current-state** — one row per entity now. No history; joins are point-in-time by accident.
- **Bridge / association** — one row per pair. Counts inflate if used as an entity table.

If there is no key, say so explicitly. "No uniqueness constraint; duplicates confirmed on
`(order_id, attempt_no)`" is a finding, and a more valuable one than any column description.

### 3. Gather evidence per object

Use what is actually available, cheapest first: DDL and comments, constraints and
indexes, data types and precision, cardinality and null counts, distinct values on low-
cardinality columns, foreign keys and lineage, existing docs and tickets, and the people who
built the table.

Sampling has limits that matter for the rubric:

- A sample of distinct values supports *"values seen include …"*, not *"allowed values are …"*.
  A categorical claim needs the code table or a full distinct count.
- Null counts from a sample are not null *semantics*. Whether `NULL` means unknown, not
  applicable, or not yet evaluated is a fact about the process, not the data.
- A type tells you `decimal(18,2)`. It does not tell you whether that is pounds or pence.

### 4. Draft the dataset description

In this order, because each line constrains the next:

1. **Summary** — one sentence: what the table is for, and its grain.
2. **One row** — the grain sentence from step 2, with the key.
3. **Time semantics** — event time vs processing time, UTC or local, snapshot or incremental.
4. **Lifecycle** — how rows arrive, are corrected, and are deleted (soft delete? restatement?).
5. **What it does not contain** — the exclusions that cause wrong joins or wrong totals
   (no cancelled orders, no test accounts, only the current version of each record).
6. **Freshness** — update cadence and the lag a consumer should expect.
7. **Caveats** — known quality issues, sentinel values, deprecated columns.

Do not write it as a table of contents for its columns — "contains `customer_id`, `status` and
38 other fields" is the most common way to fill a description field with nothing.

### 5. Draft the column descriptions

Pattern, compressed to one or two sentences:

> ⟨what it holds⟩ · ⟨unit, currency, format⟩ · ⟨allowed values or derivation⟩ ·
> ⟨what NULL means⟩ · ⟨the trap⟩

Rules that follow from a machine reader:

- **Standalone.** Do not write "see the table description". Retrieval is per object.
- **Lead with meaning, not type.** "Gross amount charged to the card, in minor units (pence)"
  beats "decimal(18,2) amount field".
- **Spell out enums.** `AUTHORISED`, `DECLINED`, `VOID` — not "the status". An agent cannot
  guess whether `VOID` is a reversal or a cancellation.
- **Name the trap where it exists.** "Superseded rows keep `is_active = false`; filter on
  `valid_to IS NULL` instead." The object most likely to be misused deserves the extra clause.
- **Never use a placeholder.** If you cannot establish the meaning, write `OPEN` with the
  question and the person to ask. That is a usable output; "various" is not.

### 6. Run the swap test

For every pair of near-neighbours — `created_at` / `updated_at`, `amount` / `net_amount`,
`status` / `state`, `customer_id` / `customer_ref` — swap their descriptions. If both still
read as true, both are too vague and at least one is dangerous.

The test is cheap, it catches the exact failure a bulk AI pass produces, and it needs no
tooling. Record the pairs you tested in the proposal.

### 7. Self-check against the rubric

Open `references/rubric.md` and score the draft. Any **blocker** means it does not go to
review, however good the prose reads. The seven blockers: no evidence, missing grain,
restatement, ambiguous units, unbounded domain, unexplained null semantics, unverified
absence or sensitivity claim.

### 8. Assemble and route

Fill `assets/description-proposal.md`. Give a verdict per object, not just for the batch, and
list what you could not describe with the owner who can. See `references/examples.md` for
three strong proposals and three instructive failures.

## Bulk mode

Scale changes the risk, not the standard. An inferred description is a hypothesis; 400 of
them is 400 hypotheses, and the plausible ones will be adopted.

- **Batch by table**, never by column type or alphabetically. Grain and context are per
  table, and a reviewer can only approve a table they know.
- **Tier every object.** `A — verified` (evidence plus an owner or documented source),
  `B — derived` (consistent with the available evidence, including an inferred meaning, but
  unconfirmed; goes to review), `C — deferred` (cannot be established; needs the owner). Only A
  is publishable.
- **Report real coverage.** "28 verified, 9 derived, 3 deferred of 40" — never "40 described".
  The second number is the one that ends up in a data-quality dashboard and gets believed.
- **Keep the deferred list.** It is a routing document, not an admission of failure: a named
  owner per deferred column is worth more than a guess.
- **Review per table.** Give the reviewer the table, its grain, the tier and the diff — not 40
  sentences to approve one at a time, which is how review becomes rubber-stamping.

## If a catalog adapter is available

Functional wording first, tool second. A catalog adapter (Collibra, Alation, Purview, DataHub,
…) handles the mechanical parts: reading existing descriptions, diffing proposed against
current text, and writing after approval.

Before overwriting, show what is being replaced and who wrote it — a human-authored description
outranks an inferred one even when it is shorter. Never bulk-write: show the diff, get explicit
confirmation, and let the audit trail record who approved what.

## Stop and escalate

Escalate to a human rather than resolving it yourself when:

- the column is regulated, contains free text, or is a candidate for special-category data;
- the table has no key, or two competing definitions of what makes a row unique;
- the meaning depends on a code table or reference data you cannot read — do not infer the
  values from the column name;
- the data contradicts an existing published definition or metric — the description may be
  right and the metric wrong, and that is a governance decision;
- the table owner disputes the observed semantics, because the data may be wrong rather than
  the description;
- the object feeds a regulatory report or a live AI use case, where a wrong description
  propagates into an output nobody will review.

## Definition of done

The grain is stated; every description has an evidence tier; units, domain and null meaning
are stated or `OPEN`; near-neighbours pass the swap test; each column description stands
alone; coverage is reported as verified and derived separately; deferred objects are named
with an owner; no unverified absence or sensitivity claim survives.
