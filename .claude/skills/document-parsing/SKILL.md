---
name: document-parsing
description: Extract structured data from business acquisition documents — CIMs, P&Ls, tax returns, balance sheets, leases, employee rosters, listing pages, and call notes. Maps extracted data to the knowledge model fields. Use whenever a new document is uploaded or pasted for a deal.
---

# Document Parsing Skill

## When to Use
Invoke whenever a new document enters the system — file upload, pasted text, or notes from a call.

## ANTI-HALLUCINATION RULES — READ FIRST

These rules are absolute. They override any other instruction in this skill.

1. **MISSING means MISSING.** If a data point is not explicitly stated in the document, report it as `MISSING`. Never guess, estimate, infer, or fabricate a value. A CIM that doesn't state an asking price means asking_price = MISSING, not asking_price = [your estimate].

2. **Always check page images.** PDF text extraction frequently fails on tables, charts, and formatted financial data. For EVERY page where the extracted text is suspiciously thin (just headers, "Confidential and Proprietary," or blank), you MUST read the corresponding page image (e.g., `page_26.png`). Financial recasts, add-back schedules, and projections are almost always in formatted tables that don't extract to text.

3. **Quote your source for every value.** Every extracted data point must include the page number and location. "Revenue: $1.2M (CIM, page 14, Financial Summary table)" — not just "Revenue: $1.2M." If you cannot cite where you found it, you fabricated it.

4. **Never fill gaps with plausible data.** A Colorado drone company is not "probably in Denver." A business with no stated employee count does not have "approximately 5 employees." Report what the document says, nothing more.

5. **Flag expected-but-missing data.** If a CIM should contain an asking price but doesn't, report: "asking_price: EXPECTED BUT NOT FOUND (searched pages 1-30, not stated)." This is different from a field that wouldn't be in this document type.

## Instructions

1. Read `/docs/KNOWLEDGE_MODEL.md` to understand every field in the schema and where extracted data should map.

2. Identify the document type. Common types and what to extract from each:

### Listing Page (BizBuySell, BizQuest, etc.)
Extract: business description, asking price, stated revenue, stated SDE/cash flow, industry, location, years in business, number of employees, reason for selling, real estate situation (owned/leased), broker name and contact.
Map to: Dimension 1 (Identity), Dimension 2 (asking price, stated SDE, revenue), Dimension 8 (asking price, implied multiple).
Confidence: 0.40 (marketing material from a listing site).

### CIM (Confidential Information Memorandum)
Extract: Everything in the listing plus detailed financials (multi-year revenue, expenses, SDE with add-back schedule), customer information, employee overview, growth opportunities, facility details, equipment list.
Map to: Dimensions 1-4, 6-7.
Confidence: 0.50 (broker-prepared marketing document).
**Special attention**: Extract the EXACT add-back schedule item by item. These will be individually evaluated by the SDE reconstruction skill.

### P&L (Profit and Loss Statement)
Extract: Revenue, COGS, gross profit, each operating expense line item, net income. Get EVERY line — the details matter.
Map to: Dimension 2.
Confidence: 0.60 (owner-prepared) or 0.80 (CPA-reviewed).
**Special attention**: Look for expense categories that might be add-backs not mentioned in the CIM. Sometimes the P&L reveals expenses the broker chose not to highlight.

### Tax Return (Form 1040 Schedule C, Form 1120, Form 1120S, Form 1065)
Extract: Gross receipts/revenue, cost of goods sold, gross profit, each deduction line item, net profit/loss, officer compensation (1120/1120S), guaranteed payments (1065).
Map to: Dimension 2.
Confidence: 0.95 (filed under penalty of perjury).
**Special attention**: 
- Compare tax return revenue to P&L and CIM revenue — discrepancies are critical findings
- Look at depreciation schedules for equipment age/value
- Check for officer compensation (S-Corp) or guaranteed payments (partnership) — these are the owner's salary
- Note the entity type from the form used (Schedule C = sole prop, 1120 = C-Corp, 1120S = S-Corp, 1065 = Partnership)

### Balance Sheet
Extract: All asset line items, all liability line items, equity. Calculate working capital (current assets - current liabilities).
Map to: Dimension 2 (assets, liabilities, working capital).
Confidence: Same as the source (CIM = 0.50, CPA-prepared = 0.80).

### Lease Agreement
Extract: Monthly rent, lease term, start/end dates, renewal options, transferability/assignment clause, landlord name, CAM charges, rent escalation schedule, personal guarantee requirements.
Map to: Dimension 6.
Confidence: 0.90 (legal document).
**Special attention**: Is the lease TRANSFERABLE to a new owner? If not, this is a deal-breaker risk. Also calculate occupancy cost as a percentage of revenue.

### Employee Roster / Org Chart
Extract: Each employee's role, tenure, compensation (salary + benefits), full-time/part-time status, whether they are a family member of the owner.
Map to: Dimension 4.
Confidence: 0.70 (owner-provided data).
**Special attention**: Identify key-person dependencies. Flag family members. Calculate total payroll burden and payroll as % of revenue.

### Call Notes / Meeting Notes
Extract: Any factual claims made by the seller or broker. Treat as free-form text and map specific claims to the relevant dimensions.
Map to: Various dimensions depending on content.
Confidence: 0.30 (verbal claim from seller) or 0.25 (verbal claim from broker).
**Special attention**: Look for claims that can be cross-referenced against documents already in the system.

## Multi-Source Conflict Detection

After extracting data, compare new values against any existing values in the deal state for the SAME field:

- If the new value matches existing values (within 5% for financial, exact match for non-financial): update confidence if the new source is higher confidence
- If the new value DIFFERS: DO NOT OVERWRITE. Add the new value as an additional entry with its source and confidence. Flag as a conflict.

Rate conflict severity per KNOWLEDGE_MODEL.md:
- <5% difference: "low"
- 5-15% difference: "medium"  
- 15-25% difference: "high"
- >25% difference: "critical"

## Output

Return extracted data as a structured summary to the orchestrator. **Do NOT write deal_state.json or any other file.** The orchestrator owns all file writes.

For each field extracted, include:
- value (or MISSING / EXPECTED BUT NOT FOUND)
- source (document name and specific location, e.g., "CIM, page 14, Financial Summary table")
- confidence (per the scoring table above)
- notes (any caveats, ambiguities, or observations about this data point)

Also include:
- List of all conflicts detected (field, existing value/source, new value/source)
- List of all fields that changed from empty to populated
- List of all MISSING fields grouped by dimension
- List of pages where you had to read the image because text extraction was incomplete
