---
name: market-research
description: Research industry trends, competitive landscape, comparable transactions, and local market conditions for a business under evaluation. Use when business identity (industry, location) is known and market context is needed, or when the user requests competitive analysis.
---

# Market Research Skill

## When to Use
Invoke when Dimension 1 (Business Identity) has enough data to identify the industry and location, or on demand when the user asks about competition or market conditions.

## Instructions

1. Read the deal state for: industry, location, business model, products/services, years in operation.

## Research Areas

### Industry Overview
Research and summarize:
- Industry size (total addressable market)
- Growth rate (is this industry growing, flat, or declining?)
- Key trends affecting the industry in the next 3-5 years
- Typical financial benchmarks: gross margins, net margins, revenue per employee
- Typical SDE multiples for businesses in this industry (use BizBuySell data, DealStats, or industry reports)
- Regulatory environment — any upcoming changes that could help or hurt

Sources to prioritize: IBISWorld, Bureau of Labor Statistics, trade association reports, recent industry analyses.

### Local Competitive Landscape
Research and summarize:
- Who are the direct competitors in the business's service area?
- How are they positioned (price, quality, specialization)?
- What do their online reviews look like? (Google Reviews, Yelp, BBB)
- Are competitors growing, stable, or declining?
- Is the market saturated or is there room for growth?
- Are there national/franchise competitors entering the local market?

### Comparable Transactions
Search for similar businesses that have sold:
- Same industry, similar size (within 50-200% of target revenue)
- Within the last 2 years
- Note: sale price, SDE, multiple achieved, location, and any deal details available
- Sources: BizBuySell sold listings, DealStats, industry-specific M&A databases

### Local Economic Conditions
Research the local market:
- Population growth trend
- Median household income and trend
- Unemployment rate
- Commercial real estate market (vacancy rates, rental trends)
- Major employers or economic developments
- Anything that affects the demand for this business's products/services locally

### For Non-Skilled Homecare Businesses Specifically
If the deal is a homecare business, also research:
- State-specific regulations (some states require registration, some don't)
- Medicaid/Medicare reimbursement rates and trends in the state
- Average revenue per caregiver in the market
- Caregiver turnover rates (industry average is 60-80% annually)
- Local competition from franchise homecare companies (Home Instead, Visiting Angels, etc.)
- Demographic trends: aging population projections for the service area

## Output Format

Write findings to Dimension 5 (Market & Competition) in the deal state. Structure as:

```
MARKET CONTEXT: [Business Name / Industry]

Industry Outlook: [Growing / Stable / Declining / Disrupted]
Industry Growth Rate: X% annually
Typical Multiples: X.Xx - X.Xx SDE

Competitive Position:
[Summary of where this business sits relative to competitors]

Comparable Transactions:
[Table of recent comparable sales if found]

Local Market:
[Summary of local economic conditions relevant to this business]

Key Market Risks:
[Specific risks from market/competitive research]

Key Market Opportunities:
[Specific opportunities identified]
```

## Rules
- Cite sources for specific data points (industry growth rates, benchmark numbers)
- Distinguish between hard data (published statistics) and estimates/inferences
- If comparable transaction data is limited, say so — don't fabricate comps
- Always note how the business under evaluation compares to benchmarks (above/below average)
