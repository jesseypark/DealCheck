---
name: financial-discrepancy
description: Detect and analyze discrepancies between financial documents — CIM vs P&L vs tax returns. Produces reconciliation tables showing where numbers differ and what the differences mean for valuation. Use whenever financial data from multiple sources is present in the deal state.
---

# Financial Discrepancy Analysis Skill

## When to Use
Invoke whenever the deal state has financial data from 2+ different sources for the same fields (e.g., revenue from both CIM and tax return, or SDE from both CIM and your reconstruction).

## Instructions

1. Read `/docs/METHODOLOGY.md` for confidence scoring and valuation impact rules.
2. Read all financial fields in the deal state, grouped by source.

## Step 1: Build the Reconciliation Table

For each financial metric that appears in multiple sources, create a year-by-year comparison:

```
REVENUE RECONCILIATION
                    CIM         P&L         Tax Return
2023 Revenue:       $X          $Y          $Z
2024 Revenue:       $X          $Y          $Z
2025 Revenue:       $X          $Y          $Z

Variances:
CIM vs P&L:         +X.X%       
CIM vs Tax:         +X.X%
P&L vs Tax:         +X.X%
```

Do this for: Revenue, COGS, Gross Profit, Total Operating Expenses, Net Income, and SDE (seller's stated vs. your reconstruction).

## Step 2: Diagnose Each Discrepancy

Common explanations for CIM vs P&L differences:
- CIM rounds or annualizes partial-year data
- CIM includes projected/pipeline revenue not yet realized
- CIM excludes returns or refunds
- Broker inflated numbers (red flag)

Common explanations for P&L vs Tax Return differences:
- Cash vs accrual accounting basis (most common — check the tax return for method used)
- Timing differences on revenue recognition
- Expenses categorized differently
- Items on the tax return not on the P&L (depreciation, amortization, home office deduction)
- Owner running personal expenses through the business differently on each document

Common explanations for CIM vs Tax Return differences (usually the largest gap):
- All of the above compounded
- Broker used the most favorable interpretation of every figure
- Actual misrepresentation (red flag if gap exceeds 15%)

For each discrepancy, note the most likely explanation AND flag if the gap is large enough to warrant verification.

## Step 3: Quantify the Valuation Impact

Show how each source's numbers produce different valuations:

```
VALUATION IMPACT AT 3.0x MULTIPLE
Based on CIM SDE ($X):        $[valuation]  →  Asking price looks [reasonable/high/low]
Based on P&L SDE ($Y):        $[valuation]  →  Deal is [overpriced/underpriced] by $[gap]
Based on Tax Return SDE ($Z): $[valuation]  →  Deal is [overpriced/underpriced] by $[gap]
```

## Step 4: Lender Reality Check

The SBA lender will use the tax return numbers. Calculate:

```
LENDER'S MATH
Tax return SDE (conservative reconstruction):  $X
Asking price:                                   $Y
SBA loan amount (80%):                          $Z
Annual debt service (10yr @ current SBA rate):  $W
DSCR:                                           X.Xx

Verdict: [Loan is feasible / Loan requires price reduction of $X / Loan requires CPA validation]
```

If the lender's math doesn't work at the asking price, calculate the maximum price the bank would support and the gap the buyer needs to bridge.

## Step 5: Bridge Analysis

If there's a gap between asking price and lender-supportable price:

```
BRIDGING THE GAP
Gap:                    $X
Options:
  Seller price reduction:    Seller reduces by $X
  Additional seller finance: Seller carries $X on standby
  Buyer equity increase:     Buyer puts in $X more cash
  CPA validation:            If CPA validates moderate SDE, gap reduces to $X
                             (Note: Low lender acceptance rate for CPA letters)
  Earnout:                   Tie $X to performance milestones
  ROBS:                      Use retirement funds for additional equity
                             (Note: Increases personal financial risk)
```

## Output

Write reconciliation tables, discrepancy analysis, valuation impact, and lender reality check to the deal state's analysis section. Flag all conflicts that need resolution via the question generator.
