#!/usr/bin/env python3
"""Deterministic valuation calculator — three views.

Computes lender's, CPA-validated, and buyer's realistic valuations
from SDE data. Multiples are inputs, not hardcoded.

Usage (CLI):
    python3 scripts/valuation_calculator.py --deal deals/aspen-fencing
    python3 scripts/valuation_calculator.py --sde-conservative 373919 --sde-moderate 391351 --price 1100000

Usage (importable):
    from valuation_calculator import three_views
    result = three_views(sde_conservative=373919, sde_moderate=391351, asking_price=1100000)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from deal_utils import load_deal


def three_views(sde_conservative, sde_moderate=None, asking_price=None,
                multiple_low=2.0, multiple_mid=2.5, multiple_high=3.0,
                buyer_replacement_costs=0, buyer_transition_costs=0):
    """Compute three valuation views.

    Args:
        sde_conservative: Weighted avg conservative SDE (verified add-backs only)
        sde_moderate: Weighted avg moderate SDE (verified + plausible). Defaults to conservative.
        asking_price: Asking price (for implied multiple calc). Optional.
        multiple_low: Low end of multiple range
        multiple_mid: Midpoint multiple
        multiple_high: High end of multiple range
        buyer_replacement_costs: Annual ongoing costs (GM salary, health, etc.)
        buyer_transition_costs: One-time first-year costs

    Returns:
        dict with all three views
    """
    if sde_moderate is None:
        sde_moderate = sde_conservative

    # View 1: Lender's View (conservative SDE, full multiple range)
    lender = {
        "label": "Lender's View (Tax Return Basis)",
        "sde_basis": "conservative_weighted",
        "sde_amount": sde_conservative,
        "multiple_range": f"{multiple_low}x-{multiple_high}x",
        "valuation_low": round(sde_conservative * multiple_low),
        "valuation_mid": round(sde_conservative * multiple_mid),
        "valuation_high": round(sde_conservative * multiple_high),
    }

    # View 2: CPA-Validated (moderate SDE, tighter multiple range)
    cpa_low = max(multiple_low, multiple_mid)  # CPA view uses mid-to-high range
    cpa = {
        "label": "CPA-Validated View",
        "sde_basis": "moderate_weighted",
        "sde_amount": sde_moderate,
        "multiple_range": f"{cpa_low}x-{multiple_high}x",
        "valuation_low": round(sde_moderate * cpa_low),
        "valuation_mid": round(sde_moderate * (cpa_low + multiple_high) / 2),
        "valuation_high": round(sde_moderate * multiple_high),
        "caveat": "Requires CPA validation letter. Not all lenders accept these.",
    }

    # View 3: Buyer's Realistic (moderate SDE minus replacement costs)
    buyer_ongoing = sde_moderate - buyer_replacement_costs
    buyer_first_year = buyer_ongoing - buyer_transition_costs
    buyer = {
        "label": "Buyer's Realistic View",
        "sde_basis": "moderate_weighted_less_replacement",
        "sde_amount": sde_moderate,
        "replacement_costs": buyer_replacement_costs,
        "transition_costs": buyer_transition_costs,
        "ongoing_cash_flow": buyer_ongoing,
        "first_year_cash_flow": buyer_first_year,
        "multiple_range": f"{cpa_low}x-{multiple_high}x",
        "valuation_low": round(buyer_ongoing * cpa_low),
        "valuation_mid": round(buyer_ongoing * (cpa_low + multiple_high) / 2),
        "valuation_high": round(buyer_ongoing * multiple_high),
    }

    result = {
        "lender_view": lender,
        "cpa_view": cpa,
        "buyer_view": buyer,
    }

    if asking_price:
        result["asking_price"] = asking_price
        result["implied_multiples"] = {
            "on_conservative_sde": round(asking_price / sde_conservative, 2) if sde_conservative else None,
            "on_moderate_sde": round(asking_price / sde_moderate, 2) if sde_moderate else None,
            "on_buyer_ongoing_cf": round(asking_price / buyer_ongoing, 2) if buyer_ongoing > 0 else None,
        }
        result["price_vs_views"] = {
            "vs_lender_mid": asking_price - lender["valuation_mid"],
            "vs_cpa_mid": asking_price - cpa["valuation_mid"],
            "vs_buyer_mid": asking_price - buyer["valuation_mid"],
        }

    return result


def format_report(result):
    lines = []
    lines.append("VALUATION ANALYSIS — THREE VIEWS")
    lines.append("=" * 55)

    if "asking_price" in result:
        lines.append(f"\nAsking Price: ${result['asking_price']:>12,.0f}")
        im = result["implied_multiples"]
        lines.append(f"  Implied on conservative SDE: {im['on_conservative_sde']:.2f}x")
        lines.append(f"  Implied on moderate SDE:     {im['on_moderate_sde']:.2f}x")
        if im.get("on_buyer_ongoing_cf"):
            lines.append(f"  Implied on buyer cash flow:  {im['on_buyer_ongoing_cf']:.2f}x")

    for key in ["lender_view", "cpa_view", "buyer_view"]:
        v = result[key]
        lines.append(f"\n{v['label'].upper()}")
        lines.append(f"  SDE Basis:    ${v['sde_amount']:>12,.0f}  ({v['sde_basis']})")
        if "replacement_costs" in v and v["replacement_costs"] > 0:
            lines.append(f"  Replacement:  ${v['replacement_costs']:>12,.0f}")
            lines.append(f"  Ongoing CF:   ${v['ongoing_cash_flow']:>12,.0f}")
        lines.append(f"  Multiples:    {v['multiple_range']}")
        lines.append(f"  Range:        ${v['valuation_low']:>12,.0f} — ${v['valuation_high']:>12,.0f}")
        lines.append(f"  Midpoint:     ${v['valuation_mid']:>12,.0f}")
        if "asking_price" in result:
            delta = result["asking_price"] - v["valuation_mid"]
            direction = "above" if delta > 0 else "below"
            lines.append(f"  vs Asking:    ${abs(delta):>12,.0f} {direction} midpoint")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Three-view valuation calculator")
    parser.add_argument("--deal", help="Path to deal folder or deal_state.json")
    parser.add_argument("--sde-conservative", type=float, help="Conservative SDE (weighted)")
    parser.add_argument("--sde-moderate", type=float, help="Moderate SDE (weighted)")
    parser.add_argument("--price", type=float, help="Asking price")
    parser.add_argument("--multiple-low", type=float, default=2.0, help="Low multiple (default: 2.0)")
    parser.add_argument("--multiple-mid", type=float, default=2.5, help="Mid multiple (default: 2.5)")
    parser.add_argument("--multiple-high", type=float, default=3.0, help="High multiple (default: 3.0)")
    parser.add_argument("--replacement", type=float, default=0, help="Annual replacement costs")
    parser.add_argument("--transition", type=float, default=0, help="One-time transition costs")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    sde_c = args.sde_conservative
    sde_m = args.sde_moderate
    price = args.price

    if args.deal:
        ds = load_deal(args.deal)
        if sde_c is None:
            sde_c = ds.sde_conservative_weighted()
        if sde_m is None:
            sde_m = ds.sde_moderate_weighted()
        if price is None:
            price = ds.asking_price()

    if sde_c is None:
        print("Error: need --sde-conservative or --deal with SDE data")
        sys.exit(1)

    result = three_views(
        sde_conservative=sde_c,
        sde_moderate=sde_m,
        asking_price=price,
        multiple_low=args.multiple_low,
        multiple_mid=args.multiple_mid,
        multiple_high=args.multiple_high,
        buyer_replacement_costs=args.replacement,
        buyer_transition_costs=args.transition,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
