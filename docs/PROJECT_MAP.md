# Project Map

## Directory Structure

```
deal-analyzer/
├── CLAUDE.md                          # Master instructions — reactive orchestration loop
├── .gitignore                         # Security: excludes /deals/, .env, databases
│
├── .claude/
│   ├── skills/                        # Domain expertise (the "how to think" layer)
│   │   ├── sde-reconstruction/        # SDE methodology, add-back rules, legitimacy scoring
│   │   ├── document-parsing/          # Extraction rules per document type (CIM, P&L, tax return, etc.)
│   │   ├── question-generation/       # Gap analysis, question prioritization, cross-reference logic
│   │   ├── financial-discrepancy/     # Multi-source reconciliation, conflict detection
│   │   ├── market-research/           # Industry analysis, competitive landscape methodology
│   │   └── deal-scorecard/            # Scorecard generation, dimension scoring, red flag summary
│   │
│   └── agents/                        # Specialist workers (READ-ONLY — return summaries, don't write files)
│       ├── document-parser.md         # Extracts structured data from documents → returns summary + agent requests
│       ├── financial-analyst.md       # Analyzes financial data → returns valuations + agent requests
│       ├── market-researcher.md       # Researches industry and competition → returns findings + agent requests
│       └── verifier.md               # Cross-checks extracted data against sources → returns verification report + agent requests
│
├── docs/                              # Project documentation
│   ├── METHODOLOGY.md                 # Due diligence methodology — the authoritative reference
│   ├── KNOWLEDGE_MODEL.md             # Data schema, confidence scoring, conflict rules
│   ├── SECURITY.md                    # Security rules — read every session
│   ├── PROJECT_MAP.md                 # This file — architecture overview
│   ├── DECISIONS.md                   # Design decisions and reasoning
│   ├── AGENTIC_ANALYSIS.md            # System assessment and redesign rationale
│   ├── HANDOFF.md                     # Current project state
│   └── SESSION_LOG.md                 # Running log of session activity
│
├── schema/
│   └── deal_state_template.json       # Template JSON for initializing new deals
│
├── scripts/
│   ├── preprocess_pdf.py              # Extract text + render page images from PDFs
│   └── init_deal.py                   # Initialize a new deal folder with template
│
└── deals/                             # NEVER COMMITTED — per-deal data
    └── [deal-name]/
        ├── raw-documents/             # Original uploaded files
        ├── preprocessed/              # Extracted text + page images from PDFs
        │   └── [Document Name]/
        │       ├── full_text.txt      # Extracted text
        │       └── page_*.png         # Rendered page images
        ├── questions/                 # Generated question lists (.md) — produced INLINE by orchestrator
        ├── scorecards/                # Deal scorecard snapshots (.md + .html) — produced INLINE by orchestrator
        └── deal_state.json            # Current knowledge model state for this deal
```

## How Things Connect — Reactive Orchestration Loop

```
YOU upload a document or add notes
    │
    ▼
ORCHESTRATOR (main Claude Code session)
reads CLAUDE.md → reads /docs/ → identifies the deal
    │
    │  Step 1: Preprocess (orchestrator runs script directly)
    ├──► python3 scripts/preprocess_pdf.py <file>
    │    extracts text, renders page images
    │
    │  Step 2: Establish ground truth (orchestrator does this, NEVER skip)
    ├──► Orchestrator reads full_text.txt + key page images
    │    Establishes: business name, location, asking price,
    │    whether financials exist and where
    │
    │  Step 3: Extract data
    ├──► Single document: orchestrator extracts inline
    │    Multiple documents: spawns document-parser agent
    │    Agent returns structured summary → orchestrator validates
    │
    │  Step 4: Verify (when parser agent did extraction or images were primary source)
    ├──► verifier agent
    │    reads: source documents + extracted data + deal_state.json
    │    returns: VERIFIED / UNVERIFIED / CONFLICTING / FABRICATED per field
    │             + cross-source conflicts + agent requests
    │    Orchestrator validates → writes verified data to deal_state.json
    │
    │  Step 5: Reactive Loop — evaluate deal state, do highest-value next action
    │
    │    ┌─────────────────────────────────────────────────────────┐
    │    │  Financial data present?                                │
    │    │  → financial-analyst (with ground-truth numbers)        │
    │    │    loads: sde-reconstruction + financial-discrepancy    │
    │    │    reads: deal_state.json ONLY (security air gap)       │
    │    │    returns: SDE, valuations, SBA feasibility            │
    │    │             + agent requests                            │
    │    │                                                         │
    │    │  Business identity available?               ┌──────┐   │
    │    │  → market-researcher              ◄─────────│  IN  │   │
    │    │    loads: market-research skill    PARALLEL  │      │   │
    │    │    searches: web for industry data           └──────┘   │
    │    │    returns: market findings, comps, competitors         │
    │    │             + agent requests                            │
    │    │                                                         │
    │    │  Agent returned AGENT_REQUESTS?                         │
    │    │  → Orchestrator evaluates, dispatches if warranted      │
    │    │                                                         │
    │    │  Enough data for scorecard?                             │
    │    │  → Orchestrator generates INLINE (.md + .html)          │
    │    │    loads: deal-scorecard skill                          │
    │    │                                                         │
    │    │  Gaps, conflicts, or red flags?                         │
    │    │  → Orchestrator generates questions INLINE (.md)        │
    │    │    loads: question-generation skill                     │
    │    └─────────────────────────────────────────────────────────┘
    │
    │  Step 6: Present
    └──► Orchestrator summarizes all results for user
```

## Key Design Principles

**Reactive, not fixed pipeline.** The orchestrator evaluates what the deal needs after every state change, rather than running the same steps for every deal. A deal with tax returns gets different treatment than a deal with one CIM.

**Orchestrator owns all file writes.** Agents are read-only. They return structured summaries; the orchestrator validates output against source documents and writes all files.

**Agent-triggered agents.** Agents can request other agents via `AGENT_REQUESTS:` in their output. The orchestrator evaluates and dispatches. This makes the system adaptive — agents collaborate through the loop rather than running in isolation.

**Verify before you trust.** The orchestrator reads source documents before spawning agents. The verifier agent provides systematic cross-checking for parser output. Agent output that contradicts source documents is rejected.

**Ground-truth prompting.** When spawning the financial-analyst, the orchestrator includes verified numbers directly in the prompt to prevent the agent's most common failure mode (fabricating input numbers).

**Security air gap.** The document-parser and verifier read raw documents and return structured data. The financial-analyst reads ONLY deal_state.json. This prevents prompt injection in seller documents from reaching the analysis layer.

**Scorecards and questions are inline.** The orchestrator generates these directly using the skills, not via agents. The deal-scorer and question-generator agents were retired after consistently producing output that had to be rewritten.

## Technology Stack

- **Runtime**: Claude Code on Mac with Pro subscription
- **Data storage**: JSON files (deal_state.json per deal) — no database server needed for v1
- **Document preprocessing**: Python scripts for PDF text extraction and page image rendering
- **Skills format**: SKILL.md files with YAML frontmatter, following Claude Code's Agent Skills standard
- **Subagent format**: Markdown files in .claude/agents/ defining each agent's role, allowed tools, and loaded skills

## What's NOT in This Project (Yet)

- No MCP servers in v1 — agents interact with deal state via file reads
- No web UI — interaction is through Claude Code CLI
- No multi-deal comparison — one deal at a time for now
- No automated BizBuySell scraping — deals are manually identified and entered
