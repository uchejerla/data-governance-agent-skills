# Examples

Calibration matters more than rules. These are the shapes to imitate and the failures to
catch. Domains vary; the patterns do not.

---

## Great: a thresholded status term

**Active Customer** (bank, retail)

> **Definition.** A party that holds at least one open, non-delinquent deposit or lending
> account with the bank as of the reference date.
>
> **Boundary.** In scope: retail parties, including sole proprietors acting in a personal
> capacity, and including customers whose only open product is a savings account.
> Out of scope: closed accounts, accounts in bankruptcy or formal workout status, internal
> test and employee-training accounts, and legal entities — use *Commercial Client*.
>
> **Examples.** Positive: a customer with a current account opened in 2019 and no missed
> payments. Positive: a customer whose only product is a 12-month fixed deposit.
> Negative: someone who closed their last account six months ago — that is a *Former
> Customer*, and the reference date is what separates the two.
>
> **Contrast.** *Prospect* — applied for a product but never onboarded. *Dormant Account
> Holder* — holds an open account with no customer-initiated transaction in 24 months;
> dormant account holders **are** active customers.

**Why it works.** "Active" is a threshold word, and the threshold is stated instead of
assumed. Exclusions point somewhere rather than just closing the door. The negative
example does the disambiguation that a paragraph of prose could not, and `Dormant` is
contrasted precisely because it is the thing people confuse with inactive.

---

## Great: meaning separated from calculation

**Net Revenue** (finance)

> **Definition.** Revenue recognised in a period after deducting returns, trade discounts
> and customer rebates.
>
> **Boundary.** In scope: all recognised revenue in the period. Out of scope: sales taxes
> and duties (recorded gross, never netted), and intercompany eliminations, which apply
> only at consolidated level — use *Net Revenue (Consolidated)*.
>
> **Calculation.** Sum of posted invoice and credit-memo lines across GL account range
> 4000–4899, excluding tax lines. Reconciles to the income statement revenue line.
>
> **Examples.** Positive: a £100 invoice with a £10 rebate contributes £90.
> Negative: total contract value signed in the period — that is *Bookings*, not revenue.
>
> **Contrast.** *Gross Revenue* — before returns and discounts. *Bookings* — contracted,
> not yet recognised.

**Why it works.** The definition survives a ledger migration; the formula lives in its own
field where it is allowed to change. The two siblings that cause the annual argument are
named and separated in one line each.

---

## Great: a term whose answer is legitimately jurisdiction-dependent

**Data Subject** (privacy)

> **Definition.** A natural person whose personal data the organisation processes, whether
> as controller or as processor on another party's behalf.
>
> **Boundary.** In scope: customers, prospective customers, website visitors, and
> applicants. Out of scope: deceased persons in jurisdictions where their data is not
> personal data — `OPEN`, confirm per jurisdiction with Legal; and legal entities, which
> are not data subjects although their representatives' data is.
>
> **Examples.** Positive: a website visitor who abandoned a form after entering an email.
> Negative: a corporate borrower — the entity is not a data subject, its signatory is.

**Why it works.** It states the controller/processor framing rather than hiding it, and it
uses `OPEN` for a real jurisdictional split instead of picking one answer and silently
being wrong in three markets. This is what honest uncertainty looks like.

---

## Great: resolving a homonym without creating a duplicate

**Client** (wealth vs commercial)

> Do **not** create a second entry. Extend the existing *Client* term with a scope split:
> *Client (Wealth)* — an individual or family office receiving advisory or discretionary
> portfolio services; and *Client (Commercial)* — a legal entity with a lending or
> treasury relationship.
>
> Each carries its own boundary and owner, and the parent term states that neither is a
> substitute for the other, because the two populations are not additive and must never be
> summed into a single "client count".

**Why this is the right output.** Same label, deliberately different populations, two
accountable owners. The failure mode is not a bad definition — it is two entries that look
like duplicates to everyone downstream, and one report that adds them together.

---

## Failing: circular, vague, and implemented

**Customer** (as usually drafted)

> "A customer is any person or entity that is a customer of the organisation, as recorded
> in the customer master table."

Three blockers in one sentence: it is **circular** (B2), it is **implemented** (B7 — the
definition is now hostage to a table), and it has **no scope and no boundary** (B3, M1) —
closed accounts, prospects and employee records are all silent decisions.

**Rewrite direction.** Replace "customer of the organisation" with the actual relationship
that qualifies (held a product, transacted, contracted), state the reference date, and
exclude prospects and closed relationships explicitly.

---

## Failing: a metric wearing a glossary entry

**Churn Rate**

> "Churn Rate is the rate at which customers churn."

**Circular** (B2) and the **wrong artifact** (M4): the moment someone implements it, they
must invent a period, a population, a definition of churn, and whether re-activated
customers count. Four silent decisions, four different numbers.

**Rewrite direction.** This is a metric. Push the concept *Churned Customer* into the
glossary — that is the genuinely ambiguous piece — and route the rate to the metric skill,
where grain, window and denominator can be stated.

---

## Failing: the everything entry

**Preferred Customer**

> "Preferred Customer means a customer who qualifies for the loyalty programme and has
> completed the onboarding process and maintains a minimum balance of £5,000 across
> eligible products, excluding accounts opened in the last 90 days, and is identified in
> the marketing platform by the gold segment tag, which is refreshed nightly."

**Five failure modes**: non-atomic (M4 — eligibility + balance + timing + segmentation),
implementation leakage (B7 — "gold segment tag"), an unstated interaction with the 90-day
exclusion (B4 — excluded from what, exactly, and for how long?), uncomfortably long (M5),
and a definition that has to be re-read to be used (M6).

**Rewrite direction.** Two terms: *Preferred Customer* (the commercial status and who holds
it) and *Eligible Balance* (what counts and what does not). The nightly refresh belongs in
lineage or a calculation field, never in a definition.

---

## The pattern, in one place

| Field | Test it must pass |
| --- | --- |
| Definition | "X is a [category] that [distinguishing property]." Readable by a new joiner. No term-in-itself, no system names. |
| Boundary | Names what is excluded **and** where that case belongs instead. |
| Threshold | Any bounded word has a number, a window, or `OPEN`. |
| Examples | 2 positive + 1 negative, from real records. The negative example is the load-bearing one. |
| Contrast | The 2 nearest terms, each separated from this one in a single line. |
| Calculation | Present only where a calculation exists, and never inside the definition. |
| Assumptions | Entity, currency, calendar, time zone, treatment of internal records. |
