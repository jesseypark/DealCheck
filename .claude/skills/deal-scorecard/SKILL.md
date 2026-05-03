---
name: deal-scorecard
description: Generate a comprehensive deal scorecard showing the current state of analysis across all 8 dimensions, red flags, valuation summary, and top priority questions. Use on demand or after major updates to the deal state.
---

# Deal Scorecard Skill

## When to Use
Invoke when the user asks for a deal summary, after major data updates, or at any point when a snapshot of the current deal evaluation is needed.

## Instructions

1. Read `/docs/METHODOLOGY.md` for red flag rules and valuation framework.
2. Read `/docs/KNOWLEDGE_MODEL.md` for dimension definitions and scoring.
3. Read the full deal state.

## Step 1: Dimension Completeness Scoring

For each of the 8 dimensions, calculate a completeness percentage based on how many fields are populated vs. total fields:

- **Business Identity & Operations** (Dimension 1): X% complete
- **Financial Performance** (Dimension 2): X% complete
- **Revenue Quality & Customer Risk** (Dimension 3): X% complete
- **Workforce & Key-Person Risk** (Dimension 4): X% complete
- **Market & Competition** (Dimension 5): X% complete
- **Physical & Legal Infrastructure** (Dimension 6): X% complete
- **Growth & Risk Outlook** (Dimension 7): X% complete
- **Deal Economics** (Dimension 8): X% complete

Overall deal clarity = weighted average (Dimension 2 and 8 weighted 2x because financial data is the core of every deal decision).

## Step 2: Red Flag Summary

Scan the deal state for every red flag defined in METHODOLOGY.md. Group them by severity:

- 🔴 **Critical** — Could be a deal-breaker. Requires immediate resolution.
- 🟡 **Warning** — Significant concern. Needs investigation but not necessarily fatal.
- 🟢 **Watch** — Minor concern. Monitor but don't overweight.

For each red flag, include:
- What was detected
- Which data triggered it
- What would resolve it (question to ask, document to request)

## Step 3: Valuation Summary

If enough financial data exists, present:

```
ASKING PRICE:                    $XXX,XXX
Seller's Stated SDE:             $XXX,XXX  (Multiple: X.Xx)

YOUR RECONSTRUCTION:
  Conservative SDE (tax basis):  $XXX,XXX  (Multiple: X.Xx)
  Moderate SDE (CPA-validatable):$XXX,XXX  (Multiple: X.Xx)
  Seller's claimed SDE:          $XXX,XXX  (Multiple: X.Xx)

VALUATION RANGES:
  Lender's View:    $XXX,XXX - $XXX,XXX
  CPA-Validated:    $XXX,XXX - $XXX,XXX
  Buyer's Realistic:$XXX,XXX - $XXX,XXX

SBA FEASIBILITY (deal costs rolled into SBA loan per standard structure):
  Total Project Cost:            $XXX,XXX   (PP + deal costs)
  Deal Costs:                    $XXX,XXX   (attorney $15K + QofE $15K + WC $100K + guarantee fee)
  SBA Loan Amount:               $XXX,XXX
  Buyer Equity (out of pocket):  $XXX,XXX
  Seller Note:                   $XXX,XXX   (6%, 10yr amort, 5yr balloon)
  Annual Total Debt Service:     $XXX,XXX   (SBA + seller note)
  Effective SDE (after $100K repl.): $XXX,XXX
  DSCR (normal years):           X.Xx
  DSCR (balloon year):           X.Xx
  Verdict:                       [Feasible / Marginal / Does not pencil]
```

The SBA feasibility section must use the standard deal structure from METHODOLOGY.md: deal costs rolled into SBA, $100K owner replacement, $20K attorney, $17K QofE, $100K working capital, 0yr standby, 5yr maturity (balloon), 10yr seller note amortization. Show both normal-year and balloon-year DSCR.

If financial data is insufficient, state what's missing and what's needed to produce valuations.

## Step 4: Unresolved Conflicts

List every conflict in the deal state that hasn't been resolved:

```
UNRESOLVED DISCREPANCIES:
1. [Field]: [Source A] says $X vs [Source B] says $Y (X% difference)
   Impact: [How this affects valuation if one vs the other is correct]
   
2. ...
```

## Step 5: Key Unknowns

List the top 5-10 most important pieces of missing information, ranked by priority:

```
CRITICAL UNKNOWNS:
1. [What's missing] — Deal-breaker potential: X/10 — Analytical unlock: X/10
   → Request: [specific document or question needed]
   
2. ...
```

## Step 6: Top 10 Critical Questions

Include up to 10 critical questions in the scorecard, drawn from the question-generation skill output (or generated inline if question generation hasn't run recently). Group by priority tier (Priority / Important). Each question should include:
- The exact question to ask (phrased conversationally for a seller/broker call)
- Why it matters (what risk or unknown it addresses)

These questions are a core part of the scorecard — they tell the user what to do next with the analysis. Always include them.

## Step 7: Overall Assessment

Provide a brief narrative assessment:
- What does this deal look like based on current data?
- What's the biggest risk right now?
- What's the most important next step?
- Is this deal worth continued pursuit based on what's known?

**Important**: Frame the assessment as "based on available data" and clearly state what's unknown. Never make a buy/no-buy recommendation — that's the user's decision. Present the facts and risks clearly so the user can decide.

## Output Format

```
═══════════════════════════════════════════════════
DEAL SCORECARD: [Business Name]
Industry: [Industry] | Location: [City, State]
Last Updated: [Date]
═══════════════════════════════════════════════════

DEAL CLARITY: XX% overall
  Business Identity:    ██████████░░  XX%
  Financial Performance:████████░░░░  XX%
  Revenue Quality:      ██████░░░░░░  XX%
  Workforce Risk:       ████░░░░░░░░  XX%
  Market & Competition: ████████████  XX%
  Physical & Legal:     ██████░░░░░░  XX%
  Growth & Risk:        ████░░░░░░░░  XX%
  Deal Economics:       ████████░░░░  XX%

RED FLAGS:
  🔴 [Critical flags]
  🟡 [Warning flags]
  🟢 [Watch items]

VALUATION SUMMARY:
  [Valuation table from Step 3]

UNRESOLVED DISCREPANCIES:
  [From Step 4]

CRITICAL UNKNOWNS:
  [From Step 5]

TOP 10 QUESTIONS TO ASK:
  Priority (Score 15+):
    1. "[Question]" → Why it matters
    ...
  Important (Score 10-14):
    6. "[Question]" → Why it matters
    ...

ASSESSMENT:
  [From Step 7]
═══════════════════════════════════════════════════
```
