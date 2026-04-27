# DealCheck

An agentic AI system for evaluating small business acquisitions, built on Claude Code.

DealCheck is a second set of eyes for deal evaluation. It extracts and structures data from whatever documents are available, detects discrepancies between sources, reconstructs Seller's Discretionary Earnings (SDE) independently, produces three valuation views, identifies red flags, and generates prioritized due diligence questions. It does not make buy/no-buy decisions.

**[Live sample scorecard](https://jesseypark.github.io/DealCheck/)** — a sanitized example of the system's output on a real deal.

## How It Works

DealCheck runs inside Claude Code as a reactive orchestration system. The main session acts as an orchestrator that reasons about what a deal needs most and dispatches specialist agents accordingly. There is no fixed pipeline — the system adapts to whatever data is available and runs every analysis the current state supports.

```
Document arrives
    → Orchestrator preprocesses and establishes ground truth
    → Extraction (inline or via document-parser agent)
    → Verification (verifier agent cross-checks against sources)
    → Orchestrator writes structured data to deal_state.json
    → Reactive loop: what's the highest-value next action?
        ├── Financial data changed? → financial-analyst
        ├── Market context needed? → market-researcher  
        ├── Enough data for a scorecard? → generate inline
        ├── Gaps or conflicts? → generate questions inline
        └── Agent requested another agent? → evaluate and dispatch
    → Loop continues until no high-value actions remain
    → Present summary
```

### The Four Agents

| Agent | Why It Exists | Error Rate |
|-------|--------------|------------|
| **document-parser** | Multi-document ingestion with cross-source conflict detection | 67% (caught by orchestrator) |
| **financial-analyst** | Deep SDE reconstruction, three valuation views, SBA feasibility | 100% on numerics (caught by orchestrator) |
| **market-researcher** | Web search for industry trends, competitors, comparable transactions | 0% |
| **verifier** | Systematic cross-check of extracted data against source documents | N/A (new) |

Yes, the financial-analyst has a 100% error rate on numeric calculations. It's also the highest-value agent in the system. More on why below.

### The Knowledge Model

Eight dimensions, 50+ fields, with multi-source conflict tracking:

1. **Business Identity & Operations** — name, entity, industry, location, employees
2. **Financial Performance** — revenue, margins, SDE (seller-stated and independently reconstructed)
3. **Revenue Quality** — customer concentration, recurring vs one-time, churn
4. **Workforce Risk** — key-person dependencies, payroll burden, owner replaceability
5. **Market & Competition** — industry size/trends, competitors, comparable transactions
6. **Physical & Legal** — lease terms, equipment condition, litigation
7. **Growth & Risk** — opportunities, capital requirements, succession readiness
8. **Deal Economics** — asking price, three valuation views, SBA loan feasibility

Every data point carries a confidence score by source type: tax returns (0.95) > bank statements (0.90) > CPA-reviewed (0.80) > owner P&Ls (0.60) > broker CIMs (0.50) > verbal claims (0.25-0.30). Values are never overwritten — when sources disagree, the discrepancy itself is the insight.

## How It Evolved

This project went through several architectural phases, each driven by real failures on real deals. The progression from "let agents do everything" to "let agents do what they're good at" is the core story.

### Phase 1: Inline Everything (Session 1-2)

The first deal was processed entirely by the main Claude Code session. No agents were spawned. The orchestrator read the CIM, extracted 200+ data points, built the scorecard, and generated questions — all inline. It worked, but wouldn't scale to multi-document deals.

### Phase 2: The 5-Agent Pipeline (Session 3)

Built a fixed pipeline with five specialist agents: document-parser, financial-analyst, market-researcher, deal-scorer, and question-generator. Every deal followed the same sequence: preprocess → extract → spawn agents → synthesize → present.

### Phase 3: Catastrophic Failure and Guardrail Overhaul (Session 4)

The second deal tested the full pipeline. The document-parser encountered a financial table rendered as an image — the extracted text showed only "Confidential and Proprietary." Instead of reporting the data as missing, the parser fabricated an entire plausible dataset: an asking price, a location, a broker name, employee counts, revenue figures, and SDE calculations. None of it existed in the document.

All four downstream agents consumed the fabricated data and produced confident-sounding but completely wrong analysis. The user caught the hallucination by questioning a specific number.

This led to a systemic overhaul:
- **Agents became read-only** — they return summaries, the orchestrator writes all files
- **Orchestrator verification became mandatory** — read source documents before spawning any agent
- **Anti-hallucination rules** were embedded in every agent definition
- **"MISSING" became the required answer** for unextractable data

### Phase 4: Agents That Keep Failing (Sessions 5-7)

Over the next four deals, a pattern emerged:

- The **deal-scorer** fabricated names, invented financial figures, built parallel schemas instead of scorecards, and ignored data that was clearly present in the deal state. Every run required the orchestrator to rewrite the output.
- The **question-generator** read stale data formats and produced questions the orchestrator always rewrote.
- The **financial-analyst** used wrong numbers on every run — fabricating officer compensation figures, misclassifying add-backs, inventing line items that didn't exist in the source documents.
- The **market-researcher** had a 0% error rate across all deals.

The orchestrator was doing double work: spawning agents and then correcting their output. For two of the five agents, the correction was a complete rewrite.

### Phase 5: Honest Assessment (Session 10)

Stepped back and asked: is this system actually agentic?

The honest answer was no. It was an **orchestrated specialist pipeline** — closer to chaining AI calls together than to agentic AI. The orchestrator followed a fixed pipeline regardless of what the deal needed. Agents were isolated one-shot workers with no communication between them. There were no feedback loops, no replanning, no information-seeking behavior.

But the system's value was real — it lived in the methodology (SDE rules, valuation framework, red flag detection), the knowledge model (8 dimensions, conflict tracking, confidence scoring), and the orchestrator's judgment (catching hallucinations, discovering things like a related-party lease buried in a document appendix). The agent architecture was the least valuable part.

### Phase 6: The Agentic Redesign (Session 8)

Four changes, each earning its slot:

1. **Reactive orchestration loop** — replaced the fixed pipeline with a reasoning loop that evaluates deal state after every change and executes the highest-value next action. A deal with tax returns gets different treatment than a deal with one CIM.

2. **Retired deal-scorer and question-generator** — both agents failed on every deal. The orchestrator generates scorecards and questions inline using the same skill files the agents were loading. Better output, fewer tokens, no correction cycle.

3. **Added a verifier agent** — systematic cross-checking that doesn't depend on the orchestrator remembering to look at the right page. Catches fabrication structurally before downstream agents see it.

4. **Agent-triggered agents** — agents can now return structured requests for other agents. The financial-analyst discovers a revenue discrepancy and requests the verifier. The market-researcher discovers a franchise and requests the financial-analyst to model franchise fees. The orchestrator evaluates each request and dispatches only when it would produce genuine value.

### Phase 7: Ground-Truth Prompting (Session 9-10)

The financial-analyst's 100% numeric error rate had a consistent cause: it would read deal_state.json, not find a number (or find it in an unexpected format), and substitute its own fabrication. The fix was **ground-truth prompting** — the orchestrator includes verified source numbers directly in the agent's prompt:

```
GROUND-TRUTH NUMBERS (use these exactly):
- 2024 officer compensation: $235,240
- 2024 net income: $22,859
- 2024 total revenue: $1,752,147

If your analysis uses a different number, STOP and explain the discrepancy.
```

On the first deal after implementing this, the financial-analyst's SDE reconstruction matched the CIM's independently calculated figure within $364. The agent still can't do arithmetic reliably, but anchoring it with verified numbers channels its analytical strength (interpreting trends, assessing add-back legitimacy, modeling scenarios) while constraining its weakness (making up inputs).

### Phase 8: Efficiency Improvements (Session 9b)

A performance postmortem on a 6-document deal revealed:
- 29% of image reads were duplicates caused by context compaction
- The document-parser misread tax return revenue by $1M+
- Interleaving image reads with agent spawns caused context overflow

Three process changes:
1. **Write to deal_state.json immediately after each page read** — no scratch files, data survives context compaction
2. **Two-phase extract-then-analyze** — complete all document extraction before spawning any analysis agents, keeping images out of context during analysis
3. **Skip the document-parser for image-based tax returns** — orchestrator direct reads are more reliable for scanned documents

## Why Not Make Everything Agentic?

The deal analysis domain has properties that work against full autonomy:

- **NDA-protected data** — every document is confidential. An autonomous agent that decides to search the web or email a broker with deal details could violate confidentiality. The human must remain the gatekeeper for external communication.
- **High cost of errors** — a fabricated SDE figure could lead to acquiring a bad business. The hallucination incident proved this isn't theoretical.
- **Irregular timing** — documents arrive when sellers send them. There's nothing for an agent to do between documents.
- **Small action space** — the system reads documents, extracts data, runs analysis, generates output. It doesn't take actions in the world that produce new information to learn from.

The system is agentic where it helps (reactive decision-making, agent-triggered agents, information-seeking during market research) and deterministic where reliability matters (the orchestrator owns all writes, verifies all output, and maintains the security air gap between raw documents and financial analysis).

The agents that survived the cuts — document-parser, financial-analyst, market-researcher, and verifier — each exist because they do something the orchestrator can't do as well on its own: multi-document cross-referencing, deep financial modeling, web research, and systematic verification. The agents that were retired — deal-scorer and question-generator — were doing tasks the orchestrator does better inline.

"More agentic" turned out to mean fewer agents doing more meaningful work, not more agents doing busywork.

## Project Structure

```
DealCheck/
├── CLAUDE.md                    # Orchestrator instructions (reactive loop, agent protocols)
├── .claude/
│   ├── agents/                  # 4 specialist agent definitions
│   └── skills/                  # 6 domain methodology files
├── schema/
│   └── deal_state_template.json # Knowledge model template
├── scripts/
│   ├── preprocess_pdf.py        # PDF → text + page images
│   └── init_deal.py             # Initialize new deal folder structure
├── docs/
│   ├── METHODOLOGY.md           # SDE rules, valuation framework, red flags
│   ├── KNOWLEDGE_MODEL.md       # 8-dimension schema specification
│   ├── SECURITY.md              # Data handling and security rules
│   └── PROJECT_MAP.md           # Architecture and folder structure
└── deals/                       # Per-deal data (gitignored, NDA-protected)
```

## Security

- All deal data lives in `/deals/` and is never committed to version control
- The financial-analyst agent never sees raw documents — only structured data in deal_state.json (air gap against prompt injection in seller documents)
- No API keys, credentials, or connection strings in any committed file
- Session-specific docs containing deal names and financials are gitignored

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with a Pro or Max subscription
- Python 3 with `pymupdf` and `Pillow` (for PDF preprocessing)

## Status

Active development. The system has been used to evaluate 6 real deals across commercial printing, drone entertainment, window coverings, auto repair, property management, and signage industries. The methodology, knowledge model, and orchestration patterns are stable. Deterministic financial calculators, tax return extraction templates, cross-deal comparison, and deal state versioning are planned for v2.
