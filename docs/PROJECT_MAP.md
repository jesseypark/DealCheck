# Project Map

## Directory Structure

```
DealCheck/
├── CLAUDE.md                          # Master instructions — reactive orchestration loop
├── README.md                          # Project overview and evolution
├── .gitignore                         # Security: excludes /deals/, .env, databases
│
├── .claude/
│   ├── skills/                        # Domain expertise (the "how to think" layer)
│   │   ├── sde-reconstruction/        # SDE methodology, add-back rules, legitimacy scoring
│   │   ├── document-parsing/          # Extraction rules per document type (CIM, P&L, tax return, etc.)
│   │   ├── question-generation/       # Gap analysis, question prioritization, cross-reference logic
│   │   ├── financial-discrepancy/     # Multi-source reconciliation, conflict detection
│   │   ├── market-research/           # Industry analysis, competitive landscape methodology
│   │   ├── deal-scorecard/            # Scorecard generation, dimension scoring, red flag summary, HTML template
│   │   └── new-deal/                  # Simplified deal initiation — file detection, folder creation
│   │
│   └── agents/                        # Specialist workers (READ-ONLY — return summaries, don't write files)
│       ├── document-parser.md         # Extracts structured data from documents (rarely used — orchestrator extracts directly)
│       ├── financial-analyst.md       # SDE reconstruction, add-back legitimacy, qualitative interpretation
│       └── market-researcher.md       # Researches industry and competition via web search
│
├── docs/                              # Project documentation
│   ├── METHODOLOGY.md                 # Due diligence methodology — the authoritative reference
│   ├── KNOWLEDGE_MODEL.md             # Data schema, confidence scoring, conflict rules
│   ├── SECURITY.md                    # Security rules — read every session
│   ├── PROJECT_MAP.md                 # This file — architecture overview
│   ├── DECISIONS.md                   # Design decisions and reasoning
│   ├── AGENTIC_ANALYSIS.md            # System assessment and redesign rationale
│   ├── PERFORMANCE_LOG.md             # Deal run metrics, waste tracking, improvement backlog
│   ├── HANDOFF.md                     # Current project state
│   └── SESSION_LOG.md                 # Running log of session activity
│
├── schema/
│   ├── deal_state_template.json       # Template JSON for initializing new deals
│   └── tax_templates/                 # Structured extraction checklists for tax returns
│       ├── form_1120s.json            # S-Corp (Form 1120-S)
│       ├── form_1065.json             # Partnership (Form 1065)
│       └── form_1040_schedule_c.json  # Sole proprietorship (Schedule C)
│
├── scripts/
│   ├── preprocess_pdf.py              # Extract text + render page images from PDFs
│   ├── init_deal.py                   # Initialize a new deal folder with template
│   ├── deal_utils.py                  # Shared deal_state.json accessor layer
│   ├── sba_calculator.py              # SBA loan feasibility, DSCR, max supportable price
│   ├── valuation_calculator.py        # Three-view valuation (lender/CPA/buyer)
│   └── sensitivity_analysis.py        # 5x5 DSCR sensitivity matrix across SDE/price variations
│
└── deals/                             # NEVER COMMITTED — per-deal data
    └── [deal-name]/
        ├── raw-documents/             # Original uploaded files
        ├── preprocessed/              # Extracted text + page images from PDFs
        │   └── [Document Name]/
        │       ├── full_text.txt      # Extracted text
        │       ├── extracted_text.json # Per-page text extraction
        │       └── page_NNN.png       # Rendered page images (zero-padded: 001, 002, ...)
        ├── extracted/                 # Structured extraction output (if used)
        ├── analysis/                  # Market research and other analysis output
        ├── questions/                 # Generated question lists (.md) — produced INLINE by orchestrator
        ├── scorecards/                # Deal scorecard snapshots (.md + .html) — produced INLINE by orchestrator
        └── deal_state.json            # Current knowledge model state for this deal
```

## How Things Connect — Reactive Orchestration Loop

```
YOU upload a document or add notes (or say "new deal")
    │
    ▼
ORCHESTRATOR (main Claude Code session)
reads CLAUDE.md → reads /docs/ → identifies the deal
    │
    │  Phase 1: EXTRACT (complete for ALL documents before Phase 2)
    │
    │  Step 1: Preprocess (orchestrator runs script directly)
    ├──► python3 scripts/preprocess_pdf.py <file>
    │    extracts text, renders page images
    │
    │  Step 2: Establish ground truth (orchestrator does this, NEVER skip)
    ├──► Orchestrator reads full_text.txt + key page images
    │    Establishes: business name, location, asking price,
    │    whether financials exist and where
    │    For tax returns: reads extraction template from schema/tax_templates/ first
    │
    │  Step 3: Extract and persist data
    ├──► Orchestrator extracts all data directly from documents
    │    Writes to deal_state.json immediately after each image read
    │    Identifies red flags, conflicts, gaps
    │
    │  Phase 2: ANALYZE (only after all extraction is complete)
    │
    │  Step 4: Reactive Loop — evaluate deal state, do highest-value next action
    │
    │    ┌─────────────────────────────────────────────────────────┐
    │    │  Financial data present?                                │
    │    │  → financial-analyst (with ground-truth numbers)        │
    │    │    reads: deal_state.json ONLY (security air gap)       │
    │    │    returns: SDE reconstruction, add-back assessment     │
    │    │             + agent requests                            │
    │    │  → Then: deterministic calculators         ┌──────┐    │
    │    │    sba_calculator.py                       │  IN  │    │
    │    │    valuation_calculator.py        ◄────────│PARALL│    │
    │    │    sensitivity_analysis.py                 │  EL  │    │
    │    │                                            └──────┘    │
    │    │  Business identity available?                           │
    │    │  → market-researcher                                   │
    │    │    searches: web for industry data                      │
    │    │    returns: executive summary + detailed findings       │
    │    │             + agent requests                            │
    │    │                                                         │
    │    │  Agent returned AGENT_REQUESTS?                         │
    │    │  → Orchestrator evaluates, dispatches if warranted      │
    │    │                                                         │
    │    │  Enough data for scorecard?                             │
    │    │  → Orchestrator generates INLINE (.md + .html)          │
    │    │    loads: deal-scorecard + question-generation skills   │
    │    │    scorecard includes up to 10 critical questions       │
    │    └─────────────────────────────────────────────────────────┘
    │
    │  Step 5: Present
    └──► Orchestrator summarizes all results for user
```

## Key Design Principles

**Reactive, not fixed pipeline.** The orchestrator evaluates what the deal needs after every state change, rather than running the same steps for every deal. A deal with tax returns gets different treatment than a deal with one CIM.

**Two-phase extract-then-analyze.** All document extraction completes before any analysis agents are spawned. This prevents context bloat from mixing image reads with agent output, which caused context compaction on early deals.

**Orchestrator owns all file writes and verification.** Agents are read-only. They return structured summaries; the orchestrator validates output against source documents and writes all files. There is no separate verifier — the orchestrator verifies during extraction and when validating agent output.

**Agent-triggered agents.** Agents can request other agents via `AGENT_REQUESTS:` in their output. The orchestrator evaluates and dispatches. This makes the system adaptive — agents collaborate through the loop rather than running in isolation.

**Ground-truth prompting.** When spawning the financial-analyst, the orchestrator includes verified numbers, add-back classifications, and broker SDE methodology context directly in the prompt. This prevents the agent's most common failure modes (fabricating input numbers, reclassifying verified add-backs, speculating about broker methodology).

**Deterministic calculators for arithmetic.** The financial-analyst handles interpretation (SDE reconstruction, add-back legitimacy, risk assessment). Python scripts handle all arithmetic (SBA feasibility, valuations, DSCR sensitivity). This division exists because the agent has strong analytical judgment but a 100% historical error rate on calculations.

**Security air gap.** The orchestrator reads raw documents and extracts structured data. The financial-analyst reads ONLY deal_state.json. This prevents prompt injection in seller documents from reaching the analysis layer.

**Scorecards and questions are inline.** The orchestrator generates these directly using the skills, not via agents. The deal-scorer and question-generator agents were retired after consistently producing output that had to be rewritten.

## Technology Stack

- **Runtime**: Claude Code on Mac with Pro subscription
- **Data storage**: JSON files (deal_state.json per deal) — no database server needed for v1
- **Document preprocessing**: Python scripts for PDF text extraction and page image rendering
- **Financial calculators**: Python scripts for SBA feasibility, valuations, and sensitivity analysis
- **Tax return extraction**: JSON template checklists for structured extraction (1120-S, 1065, 1040 Schedule C)
- **Skills format**: SKILL.md files with YAML frontmatter, following Claude Code's Agent Skills standard
- **Subagent format**: Markdown files in .claude/agents/ defining each agent's role, allowed tools, and loaded skills

## What's NOT in This Project (Yet)

- No MCP servers — agents interact with deal state via file reads
- No web UI — interaction is through Claude Code CLI
- No multi-deal comparison — one deal at a time for now (cross-deal comparison planned for v2)
- No deal state versioning — snapshots before significant updates (planned for v2)
- No automated BizBuySell scraping — deals are manually identified and entered
