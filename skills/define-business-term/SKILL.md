---
name: define-business-term
description: Use when someone asks to define, propose, review, or disambiguate a business glossary term or business concept — for example "write a definition for Active Customer", "add Net Revenue to the glossary", "is this definition any good", or "sales and finance define Client differently". Produces an evidence-grounded term proposal with a boundary statement, examples, disambiguation from neighbouring terms, ownership, sensitivity flags and an approval recommendation. Not for metric formulas, column or dataset descriptions, or policy text — route those to the metric, data-description or policy skills.
version: 0.1.0
last-reviewed: 2026-10-24
---

# Define a business term

A glossary term is a contract between teams. When it is vague, two teams build two
different numbers and the argument surfaces six months later in a board pack. Your job
is not to write a nice sentence — it is to make the term **decidable**: a competent
person reading it should reach the same answer as the term's owner about what is in and
what is out.

**Produce:** a completed term proposal using `assets/term-proposal.md`, plus a short
summary in chat.

## When to use this

| Request | Action |
| --- | --- |
| Propose a new term, or define a concept someone keeps using | This skill |
| Review or improve an existing draft definition | This skill, starting at step 6 |
| Two teams use the same word differently (homonym) | This skill — the homonym path in step 3 |
| "What does term X mean?" — answerable from the glossary | Answer the question; do not build a proposal |
| A number with a formula, grain, window or filter | It is a metric. Hand off to the metric skill |
| A column, table or dataset description | Hand off to `write-data-descriptions` |
| A policy clause or control statement | Hand off to the policy skill |
| A data domain / taxonomy node | Out of scope — taxonomy design is its own skill |

Classifying the artifact correctly is half the value. A steward asking for "Churn Rate"
usually needs a metric, not a glossary entry, and giving them a glossary entry is how
organisations end up with a definition nobody can compute.

## Non-negotiables

1. **Never invent business meaning.** Every substantive claim traces to a source —
   existing documentation, policy text, regulatory clause, a schema, a report, or a named
   subject matter expert (SME). If you cannot verify it, mark it `OPEN`. Do not soften an
   unknown into vague prose; vagueness is what you are here to remove.
2. **One concept per term.** Time grains, filters, thresholds and formulas are separate
   fields or separate artifacts. "Net Revenue QTD excluding intercompany" is a metric.
3. **Every bounded term states its bound.** Active, current, complete, valid, recent and
   material all hide a threshold. State it or mark it `OPEN`.
4. **Definitions must survive a system migration.** No table names, column names, vendor
   tools, report names or SQL in the definition field. Those belong in calculation,
   lineage or source fields, which are allowed to change.
5. **Never publish.** You produce a proposal. Approval is a governance control, not a
   formality, and it needs a named human.
6. **Record what you did not check.** A uniqueness claim without a recorded search is a
   false assurance, and false assurance is worse than a known gap.

## Procedure

### 1. Frame the request

Capture, without paraphrasing: the request verbatim, who asked, the decision or report
the term supports, who will consume it, and the candidate domain. The decision it
supports usually determines how precise the boundary must be.

### 2. Classify the artifact

Use the table above. If it is not a business term, say so plainly, explain the one-line
reason, and hand off. Do not silently produce a glossary entry for a metric.

Also note the type: **concept** (a thing — Customer, Household), **status** (a condition
— Delinquent, Active), or **measure concept** (Revenue, Exposure). Status and bounded
terms need the most boundary work.

### 3. Duplicate and homonym check

This is the step most stewards skip and the step that most often changes the answer.

Search for four things: an **exact** match, a **synonym** match (Client/Customer), a
**near-duplicate** with a different scope (Retail Customer vs Commercial Client), and a
**homonym** — same label, deliberately different meaning in another domain.

Record the surface you searched (glossary, wiki, report library, schema, ticket history)
and the result. If no catalog is reachable, ask for a glossary export, or give the user a
three-query checklist to run and report back. Never claim uniqueness without recording
the search.

If a duplicate exists, the correct output is often *"do not create a new term — extend
term X"* rather than a new proposal. Say that.

### 4. Establish the meaning from evidence

Gather evidence before drafting. Ask **at most five questions, all at once** — do not
interview the user one question at a time.

Question bank, pick the ones that actually change the definition:

- What decision or report breaks if this term is wrong?
- Which population is in scope, and which is deliberately out? (entities, jurisdictions, products, internal/test records)
- Who is authoritative here — which team or system is the system of record?
- What is the nearest thing people confuse this with, and what separates them?
- Is there a threshold, window or grain hiding in how people use the term today?
- Does this concept carry personal, financial, or regulated data?

If the user cannot answer, proceed with `OPEN` markers rather than guessing. A proposal
with three honest `OPEN` questions is more useful than a confident invention.

### 5. Draft the entry

In this order, because each field constrains the next:

1. **Definition** — 1 to 3 sentences. Pattern: *"[Term] is a [category] that
   [distinguishing property]."* Category first, then the thing that separates it from its
   siblings. No circularity, no restating the term, no synonyms dressed up as content.
2. **Boundary** — explicit in-scope and out-of-scope, naming what to use instead for the
   excluded cases.
3. **Examples** — at least two positive and one negative, drawn from real usage. The
   negative example does more disambiguation work than any sentence.
4. **Contrasting terms** — the two nearest neighbours, with a one-line difference for each.
5. **Calculation / logic** — only if the term has one. Separate field, never in the
   definition.
6. **Assumptions** — legal entity, currency, fiscal calendar, time zone, treatment of
   test/internal records.
7. **Flags** — sensitivity (personal data, financial, regulated), jurisdiction dependency,
   and whether this term feeds a published metric or AI use case.

See `references/examples.md` for three strong entries and three instructive failures.

### 6. Self-check against the rubric

Open `references/rubric.md` and score the draft. Any **blocker** means it is not
publishable, no matter how good the prose reads. Fix blockers, re-check.

The seven blockers, for quick reference: invented meaning, circularity, missing scope,
unstated threshold, no named owner, unrecorded duplicate check, implementation leakage.

### 7. Assemble and route

Fill `assets/term-proposal.md`. Set the verdict, list open questions as questions (not
as hedged prose), name the approver, and recommend one of: **Ready for review**,
**Needs SME input**, **Do not create — likely duplicate of X**.

## If a catalog adapter is available

Functional wording first, tool second. When a catalog adapter (Collibra, Alation, Purview,
DataHub, …) is present, use it for the mechanical parts: duplicate search, existing-field
lookup, and writing the approved proposal.

Never bulk-create and never write without showing the user a field-by-field diff and
getting explicit confirmation. Drafting is the skill's job; committing is a human
decision recorded in the tool's audit trail.

## Stop and escalate

Escalate to a human rather than resolving it yourself when:

- the term is regulated, or defines a regulatory report line;
- two authoritative sources genuinely conflict;
- business and finance disagree on a threshold;
- adopting the definition would change the meaning of an already-published metric;
- the same label is deliberately used differently in two domains and neither party will yield — that is a taxonomy decision, not a wording decision.

## Definition of done

The entry is decidable by someone who was not in the conversation; the boundary is
explicit; examples include a negative case; neighbours are contrasted; ownership and
approval are named; the duplicate check is recorded; unknowns are `OPEN` rather than
papered over.
