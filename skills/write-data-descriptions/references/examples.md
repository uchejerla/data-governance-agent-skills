# Examples

Descriptions fail in ways that look fine in isolation, so these are the shapes to imitate and
the failures to catch. Domains differ; the patterns do not.

---

## Great: a dataset whose grain does the work

**`payment_authorisation`** (payments)

> **Summary.** One row per authorisation attempt sent to a card issuer, including declined and
> retried attempts.
>
> **One row.** One row per attempt, uniquely identified by `attempt_id`. A retry after a
> technical failure is a **new row** with a new `attempt_id` and the same `order_id`; an order
> with four attempts has four rows. Never count rows as orders.
>
> **Time.** `authorised_at` is issuer response time in UTC. Rows are appended, never updated in
> place, except `settled_at` which arrives later.
>
> **Lifecycle.** Attempts are immutable after receipt. Settlement details arrive in a nightly
> update. There is no delete; cancelled orders keep their authorisation rows.
>
> **Not in this table.** Cancellations (see `order_event`), refunds (see `payment_refund`), and
> attempts rejected before reaching the issuer — those never leave the application and are not
> recorded here, so this table under-counts user-initiated attempts by roughly 2–3%.
>
> **Freshness.** Streaming, typically under 60 seconds. Settlement fields lag up to 24 hours.
>
> **Caveats.** Includes sandbox attempts tagged `environment = 'test'` — filter them out. Before
> March 2025, `currency` was populated from the merchant default rather than the card, so
> historical cross-currency analysis is unreliable.

**Why it works.** The grain sentence is the description: it tells you how to count, what a
retry looks like, and which totals are wrong if you ignore it. "Not in this table" answers the
question a reader actually has — why the numbers do not reconcile with the application — and
the caveat is specific enough to be actionable, including the direction and size of the known
bias.

---

## Great: four timestamps an agent will otherwise confuse

**`order`** (commerce) — column descriptions

> `created_at` — When the order record was first written by the order service, UTC. **Not** the
> customer's checkout time: orders are created when payment succeeds, which can be minutes
> later. Use `checkout_started_at` for funnel analysis.
>
> `checkout_started_at` — When the customer opened the checkout page, UTC. Null for orders
> created by the customer-service team on a customer's behalf.
>
> `updated_at` — Last time any field on the row changed, including internal pipeline updates.
> It is not a business event and moves for operational reasons; never use it as "last activity".
>
> `cancelled_at` — When the order moved to cancelled, UTC. Null means **not cancelled**, not
> "unknown" and not "cancellation date missing". Use `status = 'cancelled'` as the test, since
> a cancellation can be reversed and this field is not cleared when it is.
>
> `amount` — Order total charged, in **minor units** (pence for GBP, cents for USD), tax
> inclusive, shipping included. Divide by 100 before display. Currency is in `currency_code`;
> never sum this column across currencies without converting.

**Why it works.** Apply the swap test: swap `created_at` and `updated_at` and both become false,
because each names the mistake a reader would otherwise make. `cancelled_at` states what `NULL`
means *and* warns that the column is not a reliable test — the exact trap that makes a
plausible description actively harmful. `amount` leads with the unit, which is the one fact
that turns a 100× error into an obvious one.

---

## Great: an honest bulk result

**`gl_journal_line`** (finance) — 40 columns, one table

> **Coverage: 28 verified, 9 derived, 3 deferred.**
>
> **Grain.** One row per journal line, keyed by `(journal_id, line_no)`. A journal with eight
> lines is eight rows; a journal is balanced only when summed across all its lines.
>
> **Verified (28).** Amounts are in the ledger's functional currency, `functional_ccy`, and are
> signed: debits positive, credits negative. `posting_date` is the accounting date, which can
> differ from `created_at` by up to five days at period end. `cost_centre` values are the 14
> codes in the finance reference set, including `UNALLOCATED` for pre-allocation entries.
>
> **Derived — review queue (9).** `tax_code` and `tax_rate` were inferred from the posting
> pattern and the 2024 tax table. Consistent across 12 months of data, no owner confirmation.
> Do not use for tax reporting until confirmed.
>
> **Deferred — owner required (3).**
>
> | Column | Why deferred | Owner to ask |
> | --- | --- | --- |
> | `intercompany_flag` | Set by an upstream consolidation process that is not documented in this repo; observed values are inconsistent with the `counterparty_id` pattern | Group Consolidation (R. Okafor) |
> | `reversal_reason` | Free text, 60% null, no code table found | Financial Control (S. Mehta) |
> | `legacy_segment` | No longer populated; unclear whether historical values are meaningful | Ledger Platform (J. Lindqvist) |
>
> **Swap test run.** `posting_date` / `created_at` / `value_date`, `amount` / `functional_amount`,
> `journal_id` / `journal_line_id`. Each pair was rewritten from the other's text and rejected as
> false.

**Why it works.** It reports what it does not know. The deferred rows are more useful than the
nine derived ones, because each names a person and a reason — a reviewer can act on that today.
The coverage line cannot be mistaken for "40 done", and the table-level grain is stated before
any column claim, because every column description depends on it.

---

## Failing: the caption

**`customer.status`**

> "The status of the customer."

**`customer.customer_id`**

> "The unique identifier of the customer."

Two blockers in two lines: no information is added (B3), and the allowed values are missing
(B5) — is `status` active/inactive, or prospect/active/churned, or a lifecycle stage with six
values? The reader now knows the column exists, which they knew already, and still has to open
the code table.

**Rewrite direction.** "Lifecycle stage: `PROSPECT`, `ACTIVE`, `DORMANT`, `CHURNED`. Set by the
CRM, not derived. `DORMANT` means no customer-initiated transaction in 24 months and is
reversible." Never "the status".

A dataset-level version of the same failure is the **table of contents** description:
"Contains customer_id, status, created_at, updated_at and 38 other fields." It restates the
schema, adds nothing, and — because it names the columns — reads as though someone reviewed it.

---

## Failing: the confident inference

**`customer.is_active`**

> "Whether the customer is currently active in the system."

Written by an AI bulk pass from the column name, at scale, and it reads perfectly. It is also
wrong: this flag marks records **superseded by a merger or deduplication**. `is_active = false`
means "this row was replaced by another customer record", not "this customer left". The
customer is often still active under the surviving ID.

The consequence is concrete: an analyst filters `is_active = true` to get "active customers"
and silently drops 12% of the base, including every merged household. No error, no warning, and
a number that looks reasonable in the deck. This is the failure mode the evidence tiers exist
for — the sentence passed review because it was fluent, and no one re-opened the flag's actual
behaviour.

**Rewrite direction.** Either establish the semantics from the deduplication job and the
constraint that every superseded row has a `merged_into_id`, or mark it `C — deferred` and ask
the MDM owner. "Inferred from name; not verified" is a valid description. A confident wrong one
is not.

---

## Failing: the wiki paste

**`order_fact`**

> "This table is the core of our order analytics capability and was introduced as part of the
> 2023 platform migration. It is populated by the nightly `load_order_fact` job from the order
> service database, transformed through dbt models in the `analytics` schema, and consumed by
> the commercial dashboard and the customer 360. It supports reporting across regions and
> channels and is refreshed every night. For full details, see the Data Platform Confluence
> space, which is the source of truth. Please contact the data team with questions."

**Four failures.** No grain (B2) — the most important sentence is absent and cannot be
recovered from the rest. Pipeline internals instead of meaning (M1), including a job name that
will be renamed. Stale by design — it points at a wiki page as the source of truth, so the
description is guaranteed to disagree with it eventually (M7). And a reader still cannot answer
"how many orders were placed in March" without guessing whether a row is an order, an order
line, or an order per day.

**Rewrite direction.** "One row per order, keyed by `order_id`. Monetary values in minor units
of `currency_code`. Excludes cancelled orders before 2023 (see `order_archive`). Refresh nightly;
expect data up to 02:00 UTC." Everything about the migration belongs in a release note.

---

## The pattern, in one place

| Field | Test it must pass |
| --- | --- |
| Summary | One sentence: what the object is for, plus its grain. |
| One row | "One row per ⟨entity⟩ per ⟨event⟩, uniquely identified by ⟨key⟩." If you cannot write it, stop. |
| Columns | Business meaning, then units, then domain or derivation, then null meaning, then the trap. |
| Units | Money names its currency and minor-unit convention. Timestamps name UTC or local. |
| Domain | Enumerated, or `OPEN` with an owner. Never "various" or "the status". |
| Null | Unknown, not applicable, not yet evaluated, or not permitted. Pick one and say it. |
| Trap | The specific misuse this object invites, stated on the object, not in a wiki. |
| Evidence | A tier per object. `Inferred` is written down and reviewed, never published as fact. |
| Scale | Coverage counts verified, derived and deferred separately. The deferred list is an output. |
