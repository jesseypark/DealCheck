# Due Diligence Methodology

This document is the authoritative reference for how this system evaluates business acquisitions. Every skill and subagent should reference this methodology. If something here conflicts with a skill's instructions, this document wins.

## Financing Context

The standard deal structure is:
- 80% SBA 7(a) loan
- 10% buyer equity (cash injection)
- 10% seller financing (typically on standby for SBA requirements)

For smaller deals or when SBA terms don't work:
- ROBS (Rollover for Business Startups) — using retirement funds to capitalize the acquisition
- ROBS adds risk: retirement funds are at stake, and the IRS scrutinizes the structure

**Because SBA is the primary financing path, the lender's valuation view is the gating constraint.** If the bank won't underwrite the deal at the asking price, the deal doesn't work in its current structure. The system must always produce the lender's view first and prominently.

## SDE Reconstruction Rules

SDE (Seller's Discretionary Earnings) = Net Income + Owner Compensation + Owner Benefits + One-Time/Non-Recurring Expenses + Non-Cash Expenses + Non-Business Expenses

### Legitimate Add-Backs (rate as "verified" or "plausible")

- **Owner salary/draw**: Always legitimate. Verify against W-2s or tax returns.
- **Owner payroll taxes**: The employer portion (FICA, FUTA, SUTA) on owner compensation.
- **Owner health insurance**: If paid through the business.
- **Owner retirement contributions**: 401k, SEP-IRA, etc. paid by the business for the owner.
- **Owner vehicle expenses**: If the vehicle is primarily personal use run through the business. Requires judgment — a landscaping company owner's truck is a real business expense.
- **Depreciation and amortization**: Non-cash charges, always add back.
- **Interest expense**: Add back because the buyer will have their own debt structure.
- **One-time legal fees**: ONLY if genuinely one-time (lawsuit settlement). If legal fees appear in 2+ years, they're recurring.
- **One-time consulting/professional fees**: Same rule — must be genuinely non-recurring.

### Questionable Add-Backs (rate as "questionable" — require documentation)

- **Owner travel**: Often inflated. Require receipts or documentation showing it's truly personal travel run through the business, not business development.
- **Owner meals and entertainment**: Same issue. Some is legitimate business expense.
- **"Marketing tests"**: Sellers sometimes add back marketing spend claiming it was a one-time experiment. If the business needs marketing to maintain revenue, this is a real ongoing cost.
- **Family member salaries**: If family members work in the business, their salary is only an add-back if (a) they won't stay post-acquisition, AND (b) their role doesn't need to be replaced. If you need to hire a replacement, it's not an add-back.
- **Donations and charitable contributions**: Legitimate add-back, but verify the amounts.
- **Personal expenses run through the business**: Cell phone, home office, personal subscriptions. Legitimate in concept but often inflated in amount.

### Red Flag Add-Backs (rate as "rejected" — challenge the seller)

- **"One-time" expenses that appear in multiple years**: By definition not one-time.
- **Add-backs without documentation**: Any add-back the seller can't substantiate with receipts or records.
- **Revenue adjustments**: Sellers sometimes "add back" lost revenue from a departed customer or a bad year. Revenue is not an SDE add-back.
- **Unreasonably high owner salary add-back**: If the owner claims they pay themselves $250K in a business doing $800K revenue, verify. Compare to market rate for their role.
- **Rent to self at above-market rates**: If the owner owns the real estate and charges the business above-market rent, the delta is an add-back, but only the delta — not the full rent amount.

### SDE Reconstruction Process

1. Start from net income on the TAX RETURN (not the P&L, not the CIM)
2. Add back each item individually, rating its legitimacy
3. Calculate three SDE figures:
   - **Conservative (lender-ready)**: Only "verified" add-backs against tax return net income
   - **Moderate (CPA-validatable)**: "Verified" + "plausible" add-backs
   - **Aggressive (seller's claim)**: All add-backs including "questionable" — this should approximate the seller's stated SDE

If the seller's stated SDE doesn't approximately match the aggressive reconstruction, something is missing or fabricated.

## Three Valuation Views

### View 1: Lender's View (SBA Underwriting Basis)

- Uses: Tax return net income + verified add-backs only
- Multiple range: Depends on industry, but SBA lenders typically work with 2.5x-3.5x for most service businesses
- This view answers: "What will the bank actually lend against?"
- SBA 7(a) requires debt service coverage ratio (DSCR) of typically 1.25x
- Calculate: At the asking price with 80% SBA financing at current SBA rates (check current rate), does the conservative SDE cover the annual debt service by 1.25x?

### View 2: CPA-Validated View

- Uses: Tax return net income + verified + plausible add-backs
- This view answers: "If a CPA writes a letter validating these additional add-backs, what could the bank potentially underwrite?"
- Important caveat: CPA validation letters have a low acceptance rate with SBA lenders. Some lenders won't accept them at all. This is not a reliable path — it's an upside scenario.
- Flag to the user: "This view requires CPA validation. Not all lenders accept CPA letters, and those that do may still discount the figures."

### View 3: Buyer's Realistic View

- Uses: Moderate SDE reconstruction (verified + plausible add-backs)
- Adjusted for: Any additional costs the buyer will incur (manager salary if owner was working 50+ hours, new insurance, systems upgrades, transition costs)
- This view answers: "What will this business actually cash-flow to me after I acquire it?"
- This is the view the buyer makes their personal decision on, independent of what the bank will lend.

## ROBS Considerations

When deal size is small enough that ROBS is being considered:
- Calculate the total retirement funds at risk
- Compare to the deal's risk profile
- Flag if the deal would consume more than 60% of retirement savings (high personal risk)
- Note that ROBS structures require ongoing compliance costs ($2K-5K/year for plan administration)
- ROBS deals cannot have SBA financing simultaneously on the same entity (structure matters)

## Red Flag Detection Rules

### Financial Red Flags (auto-detect from data)

- Revenue declining year over year without explanation
- Gross margin declining while revenue is flat or growing (cost pressure)
- SDE add-backs exceeding 40% of the claimed SDE (too much discretionary spending to be credible)
- Tax return revenue differing from P&L revenue by more than 5%
- CIM revenue differing from tax return revenue by more than 10%
- Working capital is negative (business can't fund its own operations)
- Accounts receivable aging shows significant amounts 90+ days overdue
- Capital expenditures have been deferred (equipment is aging, nothing has been replaced)

### Operational Red Flags (detect from qualitative data)

- Single customer represents more than 20% of revenue (concentration risk)
- Owner works more than 50 hours/week (may need to hire a manager post-acquisition)
- Key employee has no non-compete or employment agreement
- Lease expires within 2 years with no renewal option
- Business depends on a single supplier with no alternative
- Owner has been in the business less than 3 years (limited operating history under current management)
- Family members in key roles who may leave post-acquisition

### Deal Structure Red Flags

- Asking price implies a multiple above 4x on tax-return SDE (overpriced for SBA)
- Gap between asking price and lender-supportable price exceeds 20% (hard to bridge)
- Seller unwilling to provide seller financing (lack of confidence in the business)
- Seller wants all-cash close with no transition period (running away?)

## Confidence Scoring

Every data point has a confidence score based on its source:

| Source | Base Confidence | Notes |
|--------|----------------|-------|
| Tax return (filed with IRS) | 0.95 | Highest — legal consequences for misrepresentation |
| Bank statements | 0.90 | Direct financial records |
| Audited financial statements | 0.90 | Third-party verified |
| Reviewed financial statements (CPA) | 0.80 | CPA reviewed but not audited |
| Compiled financial statements | 0.70 | CPA compiled from owner's data, no verification |
| P&L (owner-prepared) | 0.60 | Common for small businesses, no third-party verification |
| CIM (broker-prepared) | 0.50 | Marketing document — broker is incentivized to present favorably |
| Verbal claim from seller | 0.30 | Must be verified against documents |
| Verbal claim from broker | 0.25 | Broker is incentivized to close the deal |

## Industry Exclusions

The system should flag and warn (but not block) if a business falls into an excluded category:

- Licensed trades: plumbing, electrical, roofing, HVAC (requiring trade licenses)
- Licensed professions: law, medicine, dentistry, therapy/counseling, accounting (CPA)
- Restaurants and food service establishments

For non-skilled homecare businesses specifically: the system should apply homecare-specific benchmarks when available (revenue per caregiver, caregiver turnover rate, Medicaid/Medicare reimbursement rate trends, state-specific regulatory requirements that fall short of full licensing).

## Question Prioritization Logic

Questions are scored on three axes:

1. **Deal-breaker potential (0-10)**: Could the answer kill the deal?
2. **Analytical unlock value (0-10)**: How many downstream analyses does this information enable?
3. **Timing appropriateness**: "early" (first call), "mid" (after CIM review), "deep" (full due diligence)

Priority score = (deal-breaker × 1.5) + (analytical unlock × 1.0), filtered by timing.

Questions designed to cross-reference existing data (catch lies or inconsistencies) get a +3 bonus to their priority score.
