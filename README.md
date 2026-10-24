<div align="center">

<h1>Data Governance Agent Skills</h1>

<p><strong>The steward's judgment, encoded.</strong></p>

<p>Skills that make an AI agent produce governance artifacts you can put in front of an approver —<br>
not fluent text that falls apart under review.</p>

<p>
  <a href="https://github.com/uchejerla/data-governance-agent-skills/actions/workflows/validate-skills.yml"><img alt="Validate skills" src="https://github.com/uchejerla/data-governance-agent-skills/actions/workflows/validate-skills.yml/badge.svg"></a>
  <a href="https://agentskills.io"><img alt="Agent Skills format" src="https://img.shields.io/badge/format-SKILL.md-6E56CF?style=flat-square"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2EA44F?style=flat-square"></a>
  <a href="#contributing"><img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-8957E5?style=flat-square"></a>
</p>

</div>

## Install

```bash
npx skills add uchejerla/data-governance-agent-skills
```

The CLI finds every skill in the repo, asks which ones and which agent to install to, and
links them into place — project scope by default, `-g` for global. Requires Node 22.20+.

Install one specific skill to one agent:

```bash
npx skills add uchejerla/data-governance-agent-skills --skill define-business-term -a claude-code
```

See what is inside without installing anything:

```bash
npx skills add uchejerla/data-governance-agent-skills --list
```

No installer needed — every skill is a directory with a `SKILL.md`. Copy it wherever your
agent looks for skills, or read it and paste the body into a chat.

## The problem

**Vague terms are expensive.** An undefined "active customer" becomes two numbers in two
board packs, and the argument surfaces six months later with nobody able to say which one
was wrong.

**Plausible text passes review.** A definition with no boundary, no threshold and no owner
reads beautifully and fails silently. Generic assistants produce exactly that, confidently.

**Drafting was never the hard part.** The rubric, the evidence trail, and knowing which
questions must stay open — that is the job. So that is what these skills encode.

## What a skill produces

Ask *"define active customer for our retail bank"* and you get an entry whose every line
does disambiguation work:

```text
Active Customer — retail banking

Definition
  A party that holds at least one open, non-delinquent deposit or lending
  account with the bank as of the reference date.

Boundary
  In    retail parties, including sole proprietors acting in a personal
        capacity, and customers whose only open product is a savings account
  Out   closed accounts, bankruptcy or formal workout accounts, internal
        test and training accounts, and legal entities → Commercial Client

Examples
  +     current account opened 2019, no missed payments
  +     only product is a 12-month fixed deposit
  −     closed their last account six months ago → Former Customer

Contrast
  Prospect         applied for a product, never onboarded
  Dormant Holder   no customer-initiated transaction in 24 months —
                   dormant account holders ARE active customers

Verdict    Ready for review · Confidence: high · 0 blockers
```

"Active" is a threshold word, so the threshold is stated rather than assumed. Exclusions
point somewhere instead of just closing a door. The negative example does the work a
paragraph of prose cannot.

Every entry also carries its source evidence, stated assumptions, sensitivity and
jurisdiction flags, an unrecorded-duplicate check and open questions phrased for a named
person — so the approver knows precisely what they are signing.

## Skills

| Skill | Use it when | Produces |
| --- | --- | --- |
| [`define-business-term`](skills/define-business-term/SKILL.md) | Someone asks you to define, propose, review or disambiguate a business term — or two teams use the same word differently | A term proposal: definition, boundary, examples, disambiguation, ownership, flags, approval verdict |

Full catalogue, backlog and routing tests: **[SKILLS.md](SKILLS.md)**.

## How the library is built

Three layers with different lifespans. The separation is the point: the job is stable, the
tool is not.

| Layer | Lives in | Lifespan | Contains |
| --- | --- | --- | --- |
| **Functional** — the product | `skills/<name>/` | Years | Stewardship craft. Tool-agnostic. Produces reviewable artifacts. |
| **Adapters** — disposable | `skills/adapters/<capability>-<vendor>/` | Months | How to talk to a specific catalog: entities, required fields, idempotency, error handling. |
| **Standards** — shared reference | `standards/` | Years | Style guides, DQ dimensions, severity scales, regulatory control maps. |

```text
.
├── skills/                          installable — one directory per skill
│   ├── define-business-term/
│   │   ├── SKILL.md                 procedure, non-negotiables, when to use
│   │   ├── references/              rubric and examples, loaded on demand
│   │   └── assets/                  the template the skill fills in
│   └── adapters/                    installable tool adapters (planned)
├── standards/                       shared reference — not installable
├── scripts/validate_skills.py       repository checks, run by CI
├── tests/                           regression tests for the validator
├── .github/workflows/               validation on every pull request
├── SKILLS.md                        routing index
└── README.md
```

Dependency runs strictly one way: a functional skill may *mention* an adapter ("if a
catalog adapter is available, use it for the write step"), never the reverse. You should
be able to delete every adapter without losing a single lesson about how to define a term.

<sub>Adapters sit under `skills/` because that is the only place the installer looks —
verified: a top-level `adapters/` directory is not discovered, `skills/adapters/<vendor>/`
is. Losing that detail would make an entire layer invisible to users.</sub>

## The quality bar

1. **Artifact-first.** Every skill produces a concrete artifact — proposal, rule,
   assessment — useful with **zero** integrations and better with them.
2. **Review-ready, not just well written.** Outputs carry evidence, assumptions,
   confidence, and an explicit approval gate. Governance output that cannot be defended is
   worthless.
3. **Draft, never commit.** No skill writes to a production catalog without a
   field-by-field diff and explicit human confirmation. Approval is a control, not a
   formality.
4. **Rubrics, not vibes.** "You are an expert data steward" adds nothing over vanilla chat.
   Severity-labelled criteria and a blocker gate are what make fifty stewards produce the
   same answer.
5. **Record what was not checked.** Uniqueness and confidence claims carry their basis.
   False assurance is worse than a known gap.

## Compatibility

Any agent that reads the `SKILL.md` convention. The installer handles placement for Claude
Code, Cursor, Codex, OpenCode and 75+ other agents; without it, a skill is a directory you
copy.

Intentional design constraints: instructions are tool-neutral, no credentials anywhere, and
no skill depends on a vendor API to be useful.

## Conventions

### Naming

- Directory name = frontmatter `name` = kebab-case, 2–4 words.
- **Functional skills are verb-first and name the job**: `define-business-term`,
  `triage-data-quality-incident`. Not the persona (`data-steward-helper`), not a department.
- **Adapters are `<capability>-<vendor>`**: `catalog-collibra`, `catalog-alation`.
- No `-skill`, `-helper`, `-assistant` suffixes, no version numbers in names.
- One skill, one job. If the name needs "and", split it.

### Descriptions

The description is the routing layer. Most skill libraries fail here: forty skills, vague
descriptions, the agent picks the wrong one or none at all.

```text
Use when <situations in the steward's own words> — <2–4 example phrasings>.
Produces <the artifact>. Not for <adjacent jobs> — use <sibling skill>.
```

- Lead with **"Use when"**, because selection is the decision being made.
- Use the vocabulary a steward would type, not the vocabulary the library uses.
- Name the artifact, so the agent knows what success looks like.
- Always include the **negative boundary** and the handoff target.
- Target under ~700 characters.
- Test: if the description would still be true with the body deleted, it is too vague.

### Frontmatter

```yaml
---
name: define-business-term
description: ...            # routing text, formula above
version: 0.1.0              # semver
last-reviewed: 2026-10-24   # stale skills are a governance risk
---
```

Changing a rubric, a blocker or the output contract is a **major** bump — anything
downstream may now produce different answers. Adapters additionally carry `last-verified`;
unverified for 90 days means unreliable, not merely old, because stale tool knowledge is
confidently wrong.

### Definition of done

1. The description routes on real user vocabulary, and does not fire on its nearest
   sibling's.
2. It produces a named artifact, not a paragraph of advice.
3. Judgment is a severity-labelled rubric with a gate verdict; the numeric score never
   overrides a blocker.
4. Anything involving writing has ≥3 strong and ≥2 failing examples.
5. It works with no integrations, and says how it improves with one.
6. It has an explicit **never** list: publish, bulk write, invent meaning.
7. It was run against three real past cases and reviewed by someone who does the job.
8. `version` and `last-reviewed` are set.

## Roadmap

Shipped: `define-business-term`, the reference implementation for everything below.

- `write-data-descriptions` — highest volume, lowest glamour, biggest catalogue-hygiene win
- `triage-data-quality-incident` — symptom, blast radius, root cause, owner, remediation, SLA
- `classify-sensitive-data` — classification with regulatory basis and handling requirements
- `assess-data-fit-for-ai-use-case` — licensing, consent, representativeness, PII, retention

Deliberately not planned: a persona skill, and a single mega-skill covering all of
governance. Both trigger badly and neither produces an artifact.

## Contributing

Open an issue with a real case you have worked on — a term that caused an argument, a
definition that failed review, an incident that took too long to triage. Skills are built
from real failures, not from templates.

Match the conventions above. A pull request that adds a skill without examples, or that
writes to a catalog without a confirmation step, will be asked to change.

Run the same checks CI runs before opening a pull request:

```bash
python -m pip install pyyaml
python -m unittest discover -s tests -v   # the validator's own tests
python scripts/validate_skills.py
```

It verifies frontmatter and required fields, that `name` matches its directory and is
kebab-case, description length, semver and review dates, every relative link and heading
anchor, files referenced in backticks, duplicate names, and that each skill is linked from
`SKILLS.md`. The workflow fails on errors; warnings are printed but do not block.

The tests build throwaway repositories that break one rule each, so a rule cannot quietly
stop firing. If you change or add a check, add the failing fixture for it.

## License

[MIT](LICENSE).
