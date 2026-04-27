#!/usr/bin/env python3
"""
Initialize a new deal folder with the standard directory structure and a fresh deal_state.json.

Usage (run from the deal-analyzer project root):
    python scripts/init_deal.py "Smith HVAC" "https://bizbuysell.com/listing/12345"

This creates:
    deals/smith-hvac/
        raw-documents/
        preprocessed/
        extracted/
        analysis/
        questions/
        scorecards/
        deal_state.json  (from template)
"""

import json
import os
import re
import sys
from datetime import datetime


def slugify(name: str) -> str:
    """Convert a business name to a folder-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def init_deal(business_name: str, listing_url: str = ""):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deals_dir = os.path.join(project_root, "deals")
    template_path = os.path.join(project_root, "schema", "deal_state_template.json")

    # Create the deal folder
    deal_slug = slugify(business_name)
    deal_dir = os.path.join(deals_dir, deal_slug)

    if os.path.exists(deal_dir):
        print(f"Error: Deal folder already exists at {deal_dir}")
        print("If you want to start over, delete the folder first.")
        sys.exit(1)

    # Create subdirectories
    subdirs = [
        "raw-documents",
        "preprocessed",
        "extracted",
        "analysis",
        "questions",
        "scorecards",
    ]
    for subdir in subdirs:
        os.makedirs(os.path.join(deal_dir, subdir), exist_ok=True)

    # Load template and populate metadata
    with open(template_path, "r") as f:
        deal_state = json.load(f)

    deal_state["metadata"]["deal_name"] = business_name
    deal_state["metadata"]["created_date"] = datetime.now().isoformat()
    deal_state["metadata"]["last_updated"] = datetime.now().isoformat()
    deal_state["metadata"]["source_listing_url"] = listing_url

    # Write deal_state.json
    state_path = os.path.join(deal_dir, "deal_state.json")
    with open(state_path, "w") as f:
        json.dump(deal_state, f, indent=2)

    print(f"Deal initialized: {deal_dir}")
    print(f"  deal_state.json created")
    print(f"  Subdirectories: {', '.join(subdirs)}")
    print(f"")
    print(f"Next steps:")
    print(f"  1. Copy any documents into: {os.path.join(deal_dir, 'raw-documents')}/")
    print(f"  2. Open Claude Code in the deal-analyzer project")
    print(f"  3. Tell Claude: 'I have a new deal called {business_name}. Parse the documents in the raw-documents folder.'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/init_deal.py \"Business Name\" [listing_url]")
        print("Example: python scripts/init_deal.py \"Smith HVAC\" \"https://bizbuysell.com/listing/12345\"")
        sys.exit(1)

    name = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""
    init_deal(name, url)
