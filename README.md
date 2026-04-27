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

| Agent | Why It Exists |
|-------|--------------|
| **document-parser** | Multi-document ingestion with cross-source conflict detection |
| **financial-analyst** | SDE reconstruction, three valuation views, SBA feasibility, scenario modeling |
| **market-researcher** | Web search for industry trends, competitors, comparable transactions |
| **verifier** | Systematic cross-check of extracted data against source documents |

The orchestrator verifies every agent's output before persisting anything. The financial-analyst is the highest-value agent despite requiring the most correction — its strength is interpretation and pattern recognition (finding hidden revenue declines, modeling franchise fee impacts, stress-testing SBA scenarios), not arithmetic. Ground-truth prompting (described below) channels that strength while constraining its weakness.

### The Six Skills

Skills are methodology files that encode domain expertise. Agents load them for context; the orchestrator also uses them directly for inline work.

| Skill | What It Encodes |
|-------|----------------|
| **sde-reconstruction** | Add-back legitimacy rules, three SDE tiers (conservative/moderate/aggressive), owner comp handling |
| **document-parsing** | Extraction rules, anti-hallucination directives, multi-source conflict handling |
| **question-generation** | Gap analysis, prioritization scoring, integrated with an ETA due diligence reference bank |
| **financial-discrepancy** | Cross-source conflict detection patterns (CIM vs P&L vs tax returns) |
| **market-research** | Industry research methodology, comparable transaction sourcing, competitive landscape |
| **deal-scorecard** | Dimension scoring, red flag classification (critical/warning/watch), HTML template |

Skills encode methodology, not data. The scorecard and question-generation skills were originally used by dedicated agents, but those agents failed consistently — the orchestrator now generates scorecards and questions inline using the same skills, with better results.

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

Each architectural change was driven by a real failure on a real deal. The progression went from "let agents do everything" to "let agents do what they're actually good at."

### Started with a 5-agent pipeline

The first version had five specialist agents — document-parser, financial-analyst, market-researcher, deal-scorer, and question-generator — running in a fixed sequence. Every deal got the same treatment: preprocess → extract → spawn all agents → synthesize → present.

### A hallucination broke everything

On the second deal, the document-parser encountered a financial table rendered as an image. The extracted text was blank. Instead of reporting the data as missing, the parser fabricated an entire plausible dataset — asking price, location, broker name, employee counts, revenue, SDE — none of which existed in the document. All four downstream agents consumed the fabricated data and produced confident but completely wrong analysis.

This led to the system's most important architectural rule: **agents are read-only**. They return summaries; the orchestrator verifies against source documents and writes all files. Anti-hallucination rules were embedded in every agent, and "MISSING" became the mandatory answer for unextractable data.

### Two agents couldn't earn their keep

Over the next four deals, the deal-scorer and question-generator failed on every run — fabricating names, inventing figures, building parallel schemas instead of scorecards, reading stale data. The orchestrator was rewriting their entire output each time. Both were retired. The orchestrator now generates scorecards and questions inline using the same skill files, with better results and no correction cycle.

The financial-analyst had a different problem: strong analytical output (finding hidden revenue declines, modeling SBA scenarios, assessing add-back legitimacy) but unreliable numeric inputs. The market-researcher, by contrast, had a 0% error rate across all deals.

### Redesigned around what actually worked

Four changes turned the system from a fixed pipeline into something genuinely adaptive:

**Reactive orchestration loop** — the system now evaluates deal state after every change and executes the highest-value next action, rather than running the same sequence for every deal. A deal with tax returns gets different treatment than a deal with one CIM.

**Ground-truth prompting** — the financial-analyst's numeric errors had a consistent cause: it would read deal_state.json, not find a number in the expected format, and substitute a fabrication. The fix was including verified source numbers directly in the prompt:

```
GROUND-TRUTH NUMBERS (use these exactly):
- 2024 officer compensation: $235,240
- 2024 net income: $22,859
- 2024 total revenue: $1,752,147

If your analysis uses a different number, STOP and explain the discrepancy.
```

After implementing this, the financial-analyst's SDE reconstruction matched independently calculated figures within $364. The agent still needs orchestrator verification on arithmetic, but anchoring it with verified inputs channels its analytical strength while constraining its weakness.

**Agent-triggered agents** — agents can now request work from other agents through the orchestration loop. The financial-analyst discovers a revenue discrepancy and requests the verifier. The market-researcher discovers a franchise and requests the financial-analyst to model franchise fees. The orchestrator evaluates each request and dispatches only when it would produce genuine value.

**Two-phase extract-then-analyze** — a performance postmortem revealed that interleaving document image reads with agent spawns caused context overflow (29% of image reads were duplicates after compaction). Separating extraction from analysis eliminated this entirely.

The result: fewer agents doing more meaningful work, not more agents doing busywork.

## Why Not Make Everything Agentic?

The deal analysis domain has properties that work against full autonomy:

- **NDA-protected data** — every document is confidential. An autonomous agent that searches the web or contacts a broker with deal details could violate confidentiality.
- **High cost of errors** — a fabricated SDE figure could lead to acquiring a bad business. The hallucination incident proved this isn't theoretical.
- **Irregular timing** — documents arrive when sellers send them. There's nothing for an agent to do between documents.
- **Small action space** — the system reads, extracts, analyzes, and generates output. It doesn't take actions in the world that produce new information to learn from.

The system is agentic where it helps (reactive decision-making, agent-triggered agents, information-seeking during market research) and deterministic where reliability matters (the orchestrator owns all writes, verifies all output, and maintains the security air gap between raw documents and financial analysis).

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
