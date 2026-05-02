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
2. Google Drive deal folders at `/Users/jesse/Library/CloudStorage/GoogleDrive-jparktb@gmail.com/My Drive/DealCheck/Deals/` — look for new folders or files not yet processed
3. PDF/document files in the project root (`/Users/jesse/Documents/Projects/DealCheck/`)

If no files are found, ask the user where the files are.

If files were uploaded directly to the conversation (not via Google Drive), move them into the Google Drive deal folder so there's one source of truth for raw documents.

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

### Step 4 — Hand off to the standard pipeline

From here, follow the normal CLAUDE.md reactive orchestration loop. Raw documents stay in Google Drive — preprocessing reads directly from there and writes output to the local `deals/<deal>/preprocessed/` folder.

1. Preprocess all PDFs (from Google Drive path, output to local deal folder)
2. Establish ground truth (read documents yourself)
3. Phase 1: Extract all data
4. Phase 2: Analyze

The skill's job is done after Step 3. The orchestration loop handles the rest.
