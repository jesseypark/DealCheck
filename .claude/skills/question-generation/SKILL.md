---
name: question-generation
description: Generate prioritized due diligence questions based on the current deal state. Identifies gaps, conflicts, and risks, then produces questions ranked by deal-breaker potential and analytical unlock value. Use after any significant update to the deal state, or on demand.
---

# Question Generation Skill

## When to Use
Invoke after document parsing or financial analysis updates the deal state, or when the user asks "what should I ask next?"

## Instructions

1. Read `/docs/METHODOLOGY.md` — specifically "Question Prioritization Logic" for scoring rules.
2. Read the current deal state to understand what's known, what's missing, and what conflicts exist.
3. If the user's personal question lists exist in this skill's directory (e.g., `references/user-questions-*.md`), load them and integrate relevant questions that haven't been answered yet.

## Question Categories

Generate questions in these categories, then merge and rank them:

### A. Gap-Filling Questions
For each empty field in the deal state that has a priority score above 5:
- Frame a natural question that would fill the gap
- Note which downstream analyses the answer would unlock

### B. Conflict-Resolution Questions  
For each unresolved conflict in the deal state:
- Frame a question that asks the seller to explain the discrepancy
- Do NOT reveal your analysis or suspicion — phrase it neutrally
- Example: "I noticed the revenue figures differ slightly between the CIM and what I'm seeing in the financials. Can you walk me through how revenue is recognized?" (NOT: "Your CIM overstates revenue by 12%")

### C. Cross-Reference Questions
Questions designed to verify information already provided by getting the seller to state it independently:
- If you have revenue from the CIM, ask the seller verbally about revenue trajectory without referencing the specific number
- If the seller claims low owner hours, ask about their typical daily schedule in detail
- These get a +3 priority bonus per METHODOLOGY.md

### D. Red Flag Investigation Questions
For each red flag detected by the financial analyst or other agents:
- Frame a question that probes the issue without being accusatory
- Customer concentration: "Tell me about your relationship with [top customer]. How long have they been a client? Do you have a contract?"
- Revenue decline: "Walk me through what happened between [peak year] and [current year]. What changed in the market or the business?"
- High owner hours: "Describe a typical work week for you. What would need to change if you weren't here every day?"

### E. Forward-Looking Questions
Questions about risks and sustainability that no document will answer:
- "What's the biggest competitive threat you see in the next 2-3 years?"
- "If you could change one thing about the business, what would it be?"
- "What would happen to the business if you took a 6-month sabbatical tomorrow?"

## Scoring Each Question

For every question, calculate:
- **Deal-breaker potential (0-10)**: Could the answer kill the deal?
- **Analytical unlock value (0-10)**: How many analyses does this enable?
- **Cross-reference bonus**: +3 if the question is designed to catch inconsistencies
- **Priority score** = (deal-breaker × 1.5) + (analytical unlock × 1.0) + cross-reference bonus

## Timing Tags

Tag each question as appropriate for:
- **early**: First call with broker or seller. General, non-threatening, relationship-building.
- **mid**: After CIM review. More specific, financially detailed, shows you're serious.
- **deep**: Full due diligence. Detailed, potentially uncomfortable, verification-oriented.

## Output Format

Group questions into a conversation-ready format:

```
PRIORITY QUESTIONS (Score 15+)
Timing: [early/mid/deep]
1. [Question] 
   → Why it matters: [brief explanation]
   → Unlocks: [what analysis this enables]

2. [Question]
   → Why it matters: [brief explanation]
   → Unlocks: [what analysis this enables]

IMPORTANT QUESTIONS (Score 10-14)
...

HELPFUL QUESTIONS (Score 5-9)
...

CONFLICTS TO RESOLVE
1. [Conflict description]
   → Ask: [Question designed to resolve it]
   → What we know: [Source A says X, Source B says Y]
```

## Rules

- Never include more than 15 questions in a single output — prioritize ruthlessly
- Group questions that can be asked in a single conversation
- Phrase questions naturally — not like a checklist interrogation
- Never reveal your specific analysis to the seller (e.g., don't say "your multiple is 4.2x")
- Never suggest the seller is being dishonest — frame everything as seeking understanding
- If you have the user's personal question lists, check which questions from their lists are relevant to the current deal state and haven't been addressed yet
