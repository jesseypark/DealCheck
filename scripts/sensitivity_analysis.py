#!/usr/bin/env python3
"""5x5 DSCR sensitivity matrix across SDE and price variations.

Shows how DSCR changes as SDE and price move independently,
helping the buyer understand negotiation room and risk.

Usage (CLI):
    python3 scripts/sensitivity_analysis.py --deal deals/aspen-fencing
    python3 scripts/sensitivity_analysis.py --price 1100000 --sde 373919 --rate 10.5

Usage (importable):
    from sensitivity_analysis import dscr_matrix
    matrix = dscr_matrix(base_price=1100000, base_sde=373919)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from deal_utils import load_deal
from sba_calculator import sba_feasibility


def dscr_matrix(base_price, base_sde, rate_pct=10.5, term_years=10,
                price_adjustments=None, sde_adjustments=None,
                buyer_replacement_costs=0, min_dscr=1.25):
    """Generate a 5x5 DSCR sensitivity matrix.

    Args:
        base_price: Base asking price
        base_sde: Base SDE (weighted average)
        rate_pct: SBA rate
        term_years: SBA term
        price_adjustments: List of 5 price deltas (default: -20%, -10%, 0, +10%, +20%)
        sde_adjustments: List of 5 SDE deltas (default: -20%, -10%, 0, +10%, +20%)
        buyer_replacement_costs: Annual costs deducted from SDE
        min_dscr: Minimum DSCR threshold for pass/fail

    Returns:
        dict with matrix data, labels, and metadata
    """
    if price_adjustments is None:
        price_adjustments = [-0.20, -0.10, 0, 0.10, 0.20]
    if sde_adjustments is None:
        sde_adjustments = [-0.20, -0.10, 0, 0.10, 0.20]

    prices = [round(base_price * (1 + adj)) for adj in price_adjustments]
    sdes = [round(base_sde * (1 + adj)) for adj in sde_adjustments]

    price_labels = [f"${p/1000:.0f}K ({adj:+.0%})" for p, adj in zip(prices, price_adjustments)]
    sde_labels = [f"${s/1000:.0f}K ({adj:+.0%})" for s, adj in zip(sdes, sde_adjustments)]

    matrix = []
    for sde in sdes:
        row = []
        for price in prices:
            result = sba_feasibility(
                asking_price=price,
                sde=sde,
                rate_pct=rate_pct,
                term_years=term_years,
                buyer_replacement_costs=buyer_replacement_costs,
            )
            row.append({
                "dscr_post_standby": result["dscr"]["post_standby"],
                "pass": result["dscr"]["pass_post_standby"],
                "price": price,
                "sde": sde,
            })
        matrix.append(row)

    return {
        "base_price": base_price,
        "base_sde": base_sde,
        "rate_pct": rate_pct,
        "term_years": term_years,
        "buyer_replacement_costs": buyer_replacement_costs,
        "min_dscr": min_dscr,
        "price_labels": price_labels,
        "sde_labels": sde_labels,
        "matrix": matrix,
    }


def format_report(result):
    lines = []
    lines.append("DSCR SENSITIVITY MATRIX (Post-Standby)")
    lines.append("=" * 70)
    lines.append(f"Base Price: ${result['base_price']:,.0f}  |  Base SDE: ${result['base_sde']:,.0f}")
    lines.append(f"Rate: {result['rate_pct']}%  |  Term: {result['term_years']}yr  |  Min DSCR: {result['min_dscr']}x")
    if result['buyer_replacement_costs'] > 0:
        lines.append(f"Buyer Replacement Costs: ${result['buyer_replacement_costs']:,.0f}/yr")
    lines.append("")

    # Header row
    col_header = "SDE \\ Price"
    header = f"{col_header:<18}"
    for pl in result["price_labels"]:
        header += f"{pl:>14}"
    lines.append(header)
    lines.append("-" * len(header))

    for i, sde_label in enumerate(result["sde_labels"]):
        row = f"{sde_label:<18}"
        for j, cell in enumerate(result["matrix"][i]):
            dscr = cell["dscr_post_standby"]
            marker = " " if cell["pass"] else "!"
            row += f"{dscr:>12.2f}x{marker}"
        lines.append(row)

    lines.append("")
    lines.append("  ! = below minimum DSCR")

    # Find the break-even zone
    base_i = len(result["sde_labels"]) // 2
    base_j = len(result["price_labels"]) // 2
    base_dscr = result["matrix"][base_i][base_j]["dscr_post_standby"]
    lines.append(f"\n  Base case DSCR: {base_dscr:.2f}x {'(PASS)' if base_dscr >= result['min_dscr'] else '(FAIL)'}")

    # Max price at base SDE that still passes
    for j in range(len(result["price_labels"]) - 1, -1, -1):
        if result["matrix"][base_i][j]["pass"]:
            max_price = result["matrix"][base_i][j]["price"]
            lines.append(f"  Max price at base SDE that passes: ${max_price:,.0f}")
            break

    # Min SDE at base price that still passes
    for i in range(len(result["sde_labels"])):
        if result["matrix"][i][base_j]["pass"]:
            min_sde = result["matrix"][i][base_j]["sde"]
            lines.append(f"  Min SDE at base price that passes: ${min_sde:,.0f}")
            break

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="DSCR sensitivity matrix")
    parser.add_argument("--deal", help="Path to deal folder or deal_state.json")
    parser.add_argument("--price", type=float, help="Base asking price")
    parser.add_argument("--sde", type=float, help="Base SDE")
    parser.add_argument("--sde-type", choices=["conservative", "moderate"], default="conservative")
    parser.add_argument("--rate", type=float, default=10.5, help="SBA rate %%")
    parser.add_argument("--term", type=int, default=10, help="SBA term years")
    parser.add_argument("--replacement", type=float, default=0, help="Annual replacement costs")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    price = args.price
    sde = args.sde

    if args.deal:
        ds = load_deal(args.deal)
        if price is None:
            price = ds.asking_price()
        if sde is None:
            if args.sde_type == "moderate":
                sde = ds.sde_moderate_weighted()
            else:
                sde = ds.sde_conservative_weighted()

    if price is None or sde is None:
        print("Error: need --price and --sde, or --deal with populated data")
        sys.exit(1)

    result = dscr_matrix(
        base_price=price,
        base_sde=sde,
        rate_pct=args.rate,
        term_years=args.term,
        buyer_replacement_costs=args.replacement,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
