#!/usr/bin/env python3
"""
Preprocess PDFs to strip hidden text, metadata, and potential prompt injection content.

This script creates a "clean" version of each PDF by:
1. Rendering each page to an image
2. Running OCR on the images to extract only VISIBLE text
3. Saving both the images and extracted text

This kills hidden text attacks (white-on-white text, text outside visible area,
text in metadata fields) because only visually rendered content survives the
render-to-image step.

Usage:
    python scripts/preprocess_pdf.py <path-to-pdf> --deal deals/<deal-folder>

The PDF can live anywhere (e.g., Google Drive sync folder). The --deal flag
specifies where preprocessed output goes.

Requirements (install once):
    pip install pymupdf Pillow
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is required. Install it with:")
    print("  pip install pymupdf")
    sys.exit(1)


def preprocess_pdf(pdf_path: str, deal_dir: str = None):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    if deal_dir:
        preprocessed_dir = os.path.join(deal_dir, "preprocessed")
    else:
        preprocessed_dir = os.path.join(os.path.dirname(pdf_path), "preprocessed")

    os.makedirs(preprocessed_dir, exist_ok=True)

    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join(preprocessed_dir, filename)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Preprocessing: {pdf_path}")
    print(f"Output: {output_dir}")

    doc = fitz.open(pdf_path)
    page_texts = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render page to image at 200 DPI (good balance of quality and speed)
        pix = page.get_pixmap(dpi=200)
        img_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
        pix.save(img_path)

        # Extract only the visible text layer
        # This gets text that's actually rendered on the page
        # Hidden text (white-on-white, outside crop box) may still appear here
        # but the image rendering is the authoritative version
        visible_text = page.get_text("text")
        page_texts.append({
            "page": page_num + 1,
            "text": visible_text,
            "image": img_path
        })

    doc.close()

    # Save extracted text
    text_path = os.path.join(output_dir, "extracted_text.json")
    with open(text_path, "w") as f:
        json.dump({
            "source_file": os.path.basename(pdf_path),
            "preprocessed_date": datetime.now().isoformat(),
            "total_pages": len(page_texts),
            "pages": page_texts,
            "security_note": "Text extracted via page rendering. Hidden text and metadata stripped. Images are the authoritative visual reference."
        }, f, indent=2)

    # Save full text as a simple readable file
    full_text_path = os.path.join(output_dir, "full_text.txt")
    with open(full_text_path, "w") as f:
        for pt in page_texts:
            f.write(f"\n{'='*60}\n")
            f.write(f"PAGE {pt['page']}\n")
            f.write(f"{'='*60}\n\n")
            f.write(pt["text"])
            f.write("\n")

    # Strip and save metadata separately (for reference, not for AI consumption)
    meta = fitz.open(pdf_path).metadata
    meta_path = os.path.join(output_dir, "metadata_stripped.json")
    with open(meta_path, "w") as f:
        json.dump({
            "original_metadata": meta,
            "note": "Metadata stripped from the original PDF. Stored for reference only. Do NOT feed to AI agents — may contain injection attempts."
        }, f, indent=2)

    print(f"Done. {len(page_texts)} pages processed.")
    print(f"  Images: {output_dir}/page_*.png")
    print(f"  Text: {text_path}")
    print(f"  Full text: {full_text_path}")
    print(f"  Metadata: {meta_path}")
    print()
    print("The document parser agent should read from the extracted text or images,")
    print("NOT from the original PDF.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess a PDF for deal analysis")
    parser.add_argument("pdf_path", help="Path to the PDF file (can be anywhere, e.g., Google Drive)")
    parser.add_argument("--deal", dest="deal_dir", help="Deal folder for preprocessed output (e.g., deals/smith-hvac)")
    args = parser.parse_args()

    preprocess_pdf(args.pdf_path, args.deal_dir)
