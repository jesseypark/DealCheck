---
name: new-deal
description: Initialize a new deal from uploaded files. Detects unprocessed files, creates the deal folder, preprocesses documents, and starts the extraction pipeline. All files in a single upload are always for one deal.
---

# New Deal Skill

## When to Use
When the user says "new deal", drops files and asks you to analyze them, or any variation that indicates a new business acquisition to evaluate.

## Core Rule
**All files uploaded together are for ONE deal.** Never split uploads across multiple deals. Never create two deal folders from one batch of files.

## Instructions

### Step 1 — Find the files

Look for unprocessed files in these locations (check in order):
1. Files the user explicitly referenced or uploaded in this message
2. PDF/document files in the project root (`/Users/jesse/Documents/Projects/DealCheck/`)
3. Files in a `deals/` subfolder that don't belong to an existing deal's `raw-documents/` directory

If no files are found, ask the user where the files are.

### Step 2 — Get the deal folder name

If the user included a name in their initial message (e.g., "new deal Acme Services"), use that.

Otherwise, ask: "What should I call the folder for this deal?"

Do not guess from the documents. The user picks the name.

### Step 3 — Create the deal folder

Run `init_deal.py` with the business name:
```
python3 scripts/init_deal.py "Business Name"
```

If the user provided a listing URL, include it:
```
python3 scripts/init_deal.py "Business Name" "https://..."
```

### Step 4 — Move files into raw-documents

Move all uploaded files into `deals/<deal-slug>/raw-documents/`.

### Step 5 — Hand off to the standard pipeline

From here, follow the normal CLAUDE.md reactive orchestration loop:
1. Preprocess all PDFs
2. Establish ground truth (read documents yourself)
3. Phase 1: Extract all data
4. Phase 2: Analyze

The skill's job is done after Step 4. The orchestration loop handles the rest.

## What This Replaces

Previously, deal initiation required the user to either:
- Run `python3 scripts/init_deal.py "Name" "URL"` manually
- Tell the orchestrator the business name, listing URL, and which files to process

Now: drop files, say "new deal", everything else is automatic.
