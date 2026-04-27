---
name: sde-reconstruction
description: Reconstruct Seller's Discretionary Earnings from financial documents. Use when analyzing P&Ls, tax returns, or CIMs that contain financial data. Rates each add-back for legitimacy and produces conservative, moderate, and aggressive SDE figures plus three valuation views (lender, CPA-validated, buyer).
---

# SDE Reconstruction Skill

## When to Use
Invoke this skill whenever financial data changes in the deal state — new P&L uploaded, tax return received, CIM financials extracted, or any add-back information updated.

## Instructions

1. Read `/docs/METHODOLOGY.md` — specifically the "SDE Reconstruction Rules" and "Three Valuation Views" sections. That document is the authority on legitimacy ratings and reconstruction methodology.

2. Read the current deal state to get all financial fields and their sources.

3. Perform the reconstruction:

### Step 1: Identify the Base
- Use tax return net income as the base if available (highest confidence)
- If only P&L is available, use P&L net income but note lower confidence
- If only CIM is available, use CIM figures but flag everything as low confidence
- NEVER average multiple sources — reconstruct separately from each source and show the comparison

### Step 2: Itemize Every Add-Back
For each claimed add-back, create an entry with:
- **Item name**: What is being added back
- **Amount**: Dollar amount
- **Legitimacy rating**: verified / plausible / questionable / rejected (use rules in METHODOLOGY.md)
- **Reasoning**: Why you rated it this way — be specific
- **Source**: Which document this came from
- **Documentation status**: Is there supporting documentation, or is it just a claim?

### Step 3: Calculate Three SDE Figures
- **Conservative (sde_conservative)**: Net income from tax return + only "verified" add-backs
- **Moderate (sde_moderate)**: Net income + "verified" + "plausible" add-backs
- **Aggressive (sde_aggressive)**: Net income + all add-backs including "questionable"

### Step 4: Compare to Seller's Claim
- Calculate the gap between sde_aggressive and the seller's stated SDE
- If sde_aggressive < seller's stated SDE, something is missing or fabricated — flag this prominently
- If sde_aggressive > seller's stated SDE, the seller may be undervaluing (rare but check for errors)

### Step 5: Produce Three Valuation Views
Follow the methodology in METHODOLOGY.md for each view:
- **Lender's view**: Conservative SDE × industry-appropriate multiple range
- **CPA-validated view**: Moderate SDE × multiple range, with caveat about acceptance rates
- **Buyer's realistic view**: Moderate SDE adjusted for post-acquisition costs (manager salary if needed, new insurance, transition costs, etc.)

### Step 6: SBA Loan Feasibility
If asking price is known:
- Calculate loan amount at 80% of asking price
- Estimate annual debt service at current SBA 7(a) rates (10-year term)
- Calculate DSCR (Debt Service Coverage Ratio) = Conservative SDE / Annual Debt Service
- Flag if DSCR < 1.25 (SBA minimum) — the deal does not pencil at this price with SBA financing

## Output Format
Write the full sde_reconstructed object to the deal state, plus update the Deal Economics dimension with valuation views and SBA feasibility.

## Red Flags to Auto-Detect
- Add-backs exceed 40% of claimed SDE
- "One-time" items appear in 2+ years of data
- Owner salary add-back is implausibly high relative to revenue
- No documentation for add-backs representing more than $10K each
- Seller's stated SDE cannot be replicated even with all add-backs included
