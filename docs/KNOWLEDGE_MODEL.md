# Knowledge Model Schema

This document defines the data structure for every deal. The system is state-driven: at any moment, any field can be empty, partially filled, or populated from multiple sources. The system runs whatever analysis the current data supports.

## Core Principle: Multi-Source Fields

Every data field can have multiple values from different sources. Values are NEVER overwritten — new sources are appended. This is how the system detects discrepancies.

```
field_name: [
  { value: ..., source: "document name", confidence: 0.0-1.0, timestamp: "ISO date", notes: "" }
]
```

When a field has multiple values:
- The system flags it as a conflict if values differ by more than 5% (financial) or are contradictory (non-financial)
- The financial analyst determines which value to use in each valuation view
- The question generator creates questions to resolve the conflict

## Dimension 1: Business Identity & Operations

| Field | Type | Description |
|-------|------|-------------|
| business_name | string | Name of the business |
| dba_names | string[] | Any "doing business as" names |
| entity_type | string | LLC, S-Corp, C-Corp, Sole Prop, Partnership |
| industry | string | Primary industry classification |
| industry_excluded | boolean | Does this business fall in an excluded category? |
| naics_code | string | NAICS code if known |
| location_city | string | City |
| location_state | string | State |
| location_zip | string | ZIP code |
| years_in_operation | number | Years the business has existed |
| years_current_owner | number | Years under current ownership |
| owner_role | string | What the owner actually does day-to-day |
| owner_hours_per_week | number | Hours the owner works per week |
| num_employees_ft | number | Full-time employees |
| num_employees_pt | number | Part-time employees |
| products_services | string | Description of what the business sells/does |
| business_model | string | B2B, B2C, recurring, project-based, etc. |
| key_systems_software | string[] | Critical systems the business runs on |
| licenses_permits | string[] | Required licenses or permits |
| intellectual_property | string | Any IP, patents, trademarks |
| reason_for_selling | string | Why the owner is selling |
| seller_timeline | string | Desired closing timeline |

## Dimension 2: Financial Performance

| Field | Type | Description |
|-------|------|-------------|
| revenue_by_year | {year: number, amount: number}[] | Revenue for each available year |
| cogs_by_year | {year: number, amount: number}[] | Cost of goods sold by year |
| gross_margin_by_year | {year: number, pct: number}[] | Gross margin percentage by year |
| operating_expenses_by_year | {year: number, amount: number}[] | Total opex by year |
| opex_breakdown | {category: string, amount: number}[] | Opex by category for most recent year |
| net_income_by_year | {year: number, amount: number}[] | Net income by year |
| sde_seller_stated | number | SDE as claimed by seller/broker |
| sde_reconstructed | object | System's independent SDE reconstruction (see SDE schema below) |
| cash_flow_operations | number | Cash from operations if available |
| total_assets | number | Balance sheet total assets |
| total_liabilities | number | Balance sheet total liabilities |
| current_assets | number | Current assets (cash, AR, inventory) |
| current_liabilities | number | Current liabilities (AP, current debt) |
| working_capital | number | Current assets - current liabilities |
| ar_aging | object | Accounts receivable aging schedule |
| inventory_value | number | Inventory on hand |
| capex_by_year | {year: number, amount: number}[] | Capital expenditures by year |
| deferred_capex | string | Description of deferred maintenance or needed equipment |
| debt_schedule | {type: string, balance: number, payment: number, rate: number}[] | Outstanding debts |
| equipment_leases | {item: string, payment: number, remaining_term: string}[] | Equipment lease obligations |

### SDE Reconstruction Schema

```
sde_reconstructed: {
  base_year: number,
  net_income_source: "tax_return" | "pl" | "cim",
  net_income: number,
  addbacks: [
    {
      item: string,
      amount: number,
      legitimacy: "verified" | "plausible" | "questionable" | "rejected",
      reasoning: string,
      source: string,
      documentation: "documented" | "undocumented"
    }
  ],
  sde_conservative: number,    // verified add-backs only
  sde_moderate: number,        // verified + plausible
  sde_aggressive: number,      // all including questionable
  sde_seller_gap: number,      // difference between seller's stated and our aggressive
  sde_seller_gap_explanation: string
}
```

## Dimension 3: Revenue Quality & Customer Risk

| Field | Type | Description |
|-------|------|-------------|
| customer_concentration | {name: string, pct_revenue: number}[] | Top customers by revenue % |
| customer_count_total | number | Total number of active customers |
| revenue_recurring_pct | number | Percentage of revenue that is recurring/contracted |
| revenue_onetime_pct | number | Percentage that is project/one-time |
| contract_terms | string | Typical contract length and terms |
| renewal_rate | number | Contract renewal/retention rate |
| customer_acquisition_cost | number | Cost to acquire a new customer |
| acquisition_channels | string[] | How customers find the business |
| churn_rate | number | Annual customer churn |
| pipeline_backlog | number | Value of signed but undelivered work |
| seasonality | string | Description of seasonal revenue patterns |
| revenue_trend | string | "growing" | "flat" | "declining" with explanation |

## Dimension 4: Workforce & Key-Person Risk

| Field | Type | Description |
|-------|------|-------------|
| employees | {role, tenure_years, compensation, benefits, is_key_person, is_family, flight_risk, has_noncompete}[] | Full employee roster |
| total_payroll_burden | number | Total compensation + benefits + payroll taxes |
| payroll_as_pct_revenue | number | Payroll burden / Revenue |
| key_person_dependencies | string[] | People who hold critical knowledge or relationships |
| owner_replaceability | string | What happens if the owner disappears for 6 months |
| manager_salary_market | number | Market rate for a hired manager to replace the owner |
| hiring_difficulty | string | How hard is it to hire for critical roles locally |
| employment_agreements | string | Are there employment agreements or non-competes |
| post_acquisition_retention_risk | string | Who might leave after ownership change |

## Dimension 5: Market & Competition

| Field | Type | Description |
|-------|------|-------------|
| industry_size | string | Total addressable market |
| industry_growth_rate | number | Annual growth rate |
| industry_outlook | string | Growing, stable, declining, disrupted |
| direct_competitors | {name, positioning, estimated_size}[] | Key competitors |
| competitive_moat | string | What protects this business (brand, location, relationships, IP, switching costs) |
| regulatory_environment | string | Current and upcoming regulatory factors |
| technology_disruption_risk | string | Is technology threatening this business model |
| market_share_estimate | string | Rough market share if estimable |
| local_economic_conditions | string | Population trends, commercial development, etc. |
| comparable_transactions | {business, price, sde, multiple, date}[] | Similar businesses that have sold |

## Dimension 6: Physical & Legal Infrastructure

| Field | Type | Description |
|-------|------|-------------|
| real_estate_type | "owned" | "leased" | Type of real estate arrangement |
| lease_terms | {monthly_rent, expiration, renewal_options, transferable, landlord_relationship} | Lease details |
| occupancy_cost_pct_revenue | number | Rent / Revenue |
| facility_condition | string | Condition of the physical space |
| equipment_condition | string | Condition of key equipment |
| zoning_compliance | string | Any zoning issues |
| environmental_issues | string | Any environmental concerns |
| pending_litigation | string | Current or threatened lawsuits |
| litigation_history | string | Past lawsuits and outcomes |
| insurance_coverage | string | Current coverage types and adequacy |
| insurance_claims_history | string | Past claims |
| regulatory_compliance | string | Current compliance status |

## Dimension 7: Growth & Risk Outlook

| Field | Type | Description |
|-------|------|-------------|
| growth_opportunities_seller | string[] | What the seller says the growth opportunities are |
| growth_opportunities_assessed | string[] | Our independent assessment of growth potential |
| capital_required_for_growth | number | Investment needed to pursue growth |
| risks_seller_identified | string[] | Risks the seller acknowledges |
| risks_independently_identified | string[] | Risks we've found that the seller hasn't mentioned |
| business_continuity | string | What happens without the owner |
| supplier_dependencies | {supplier, critical, sole_source, alternative}[] | Key supplier relationships |
| technology_obsolescence_risk | string | Risk of systems or methods becoming outdated |
| succession_readiness | string | How ready is the business for ownership transition |

## Dimension 8: Deal Economics

| Field | Type | Description |
|-------|------|-------------|
| asking_price | number | Seller's asking price |
| implied_multiple_seller_sde | number | Asking price / seller's stated SDE |
| implied_multiple_conservative_sde | number | Asking price / our conservative SDE |
| valuation_lender_view | {low, mid, high, multiple_range} | Lender's valuation range |
| valuation_cpa_view | {low, mid, high, multiple_range} | CPA-validated range |
| valuation_buyer_view | {low, mid, high, multiple_range} | Buyer's realistic range |
| sba_loan_feasibility | {loan_amount, annual_payment, dscr, feasible} | SBA loan math |
| robs_feasibility | {retirement_funds_needed, pct_of_savings, risk_assessment} | ROBS analysis if applicable |
| seller_financing | {available, amount, terms, standby} | Seller financing details |
| estimated_working_capital_needed | number | Cash needed beyond purchase price |
| total_acquisition_cost | number | Purchase + working capital + transition + immediate capex |
| transition_plan | string | Seller's transition/training commitment |
| noncompete | string | Non-compete terms |

## Gap Tracking

The system maintains a priority-ranked list of empty fields. Priority is calculated per METHODOLOGY.md (deal-breaker potential × 1.5 + analytical unlock value, with cross-reference bonus).

## Conflict Tracking

When a field has multiple values that differ beyond threshold:

```
conflict: {
  field: string,
  values: [{ value, source, confidence }],
  severity: "low" | "medium" | "high" | "critical",
  resolved: boolean,
  resolution: string | null
}
```

Severity levels:
- **low**: Values differ by less than 5% — likely rounding or timing
- **medium**: Values differ by 5-15% — could be accounting method differences
- **high**: Values differ by 15-25% — requires explanation
- **critical**: Values differ by more than 25% — potential misrepresentation
