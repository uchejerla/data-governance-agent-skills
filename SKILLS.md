# Skill index

The routing table. One row per skill: what it is for, what it produces, and what it needs.
Conventions for adding a row are in the [README](README.md#conventions).

## Available

| Skill | Produces | Triggers on | Needs |
| --- | --- | --- | --- |
| [`define-business-term`](skills/define-business-term/SKILL.md) | A term proposal: definition, boundary, examples, disambiguation, ownership, sensitivity flags, approval verdict | "define active customer", "add net revenue to the glossary", "is this definition any good", "sales and finance define client differently" | Nothing. Optional catalog adapter for duplicate search and publishing the approved entry |
| [`write-data-descriptions`](skills/write-data-descriptions/SKILL.md) | A description proposal: grain and key, per-column meaning, units, domain values, null semantics, caveats, swap test, evidence tier per object | "describe this table", "backfill descriptions for the finance schema", "why does the AI pick the wrong column", "is this column description good enough" | Nothing. Optional catalog adapter for reading existing descriptions and writing the approved diff |

Two skills, each the reference implementation for its artifact type: a business concept, and
the metadata on a physical object. Coverage is not the moat; the quality of the encoded
judgment is.

## Planned

Backlog, not commitments. Each is listed with the artifact it would own, because two skills
that produce the same artifact will collide.

| Skill | Produces | Notes |
| --- | --- | --- |
| `triage-data-quality-incident` | Incident record: symptom, blast radius, likely root cause, owner, remediation, SLA clock | Needs a severity scale; benefits from lineage access |
| `assess-data-fit-for-ai-use-case` | Fit assessment: licensing, consent, representativeness, freshness, PII minimisation, retention | The differentiator. Chains off classification |
| `classify-sensitive-data` | Classification decision with regulatory basis and handling requirements | Feeds the AI fit assessment and the term proposal's sensitive flag |
| `design-dq-rule` | Rule specification: dimension, threshold, grain, owner, alert route | Pairs with `triage-data-quality-incident` |
| `analyse-change-impact` | Impact assessment for a schema or definition change: affected consumers, reports, models | Requires lineage; falls back to a stakeholder checklist |
| `map-regulation-to-control` | Obligation-to-control map with evidence expectations | EU AI Act, NIST AI RMF, ISO/IEC 42001 are the obvious first mappings |

Two candidates deliberately **not** planned yet: a persona skill ("data steward assistant")
and a single mega-skill covering governance. Both trigger badly and neither produces an
artifact.

## Routing tests

Before adding a skill, check it against the nearest neighbour:

| Ambiguous request | Correct owner |
| --- | --- |
| "Define Churn Rate" | Metric skill — it has grain, window and denominator |
| "Define Churned Customer" | `define-business-term` — the concept is the ambiguous part |
| "What does this column mean?" | `write-data-descriptions` — the artifact is metadata on a physical object |
| "What does 'active customer' mean in this table?" | `define-business-term` — the concept is the artifact; the column description then cites it |
| "The AI keeps summing amount across currencies" | `write-data-descriptions` — the fix is the unit rule, not a new term |
| "Why is `is_active` false for customers who never left?" | `write-data-descriptions`, starting at evidence gathering — a wrong description is a metadata defect, not a glossary question |
| "Can we use this table for our RAG index?" | `assess-data-fit-for-ai-use-case` |
| "Is this column PII?" | `classify-sensitive-data` |
| "This definition is wrong" | `define-business-term`, starting at self-check |

When a request genuinely straddles two skills, the rule is: the skill that owns the
**artifact** owns the request, and it may consume the other's output.
