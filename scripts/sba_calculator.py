#!/usr/bin/env python3
"""Deterministic SBA loan feasibility calculator.

Computes debt service, DSCR, and max supportable price for standard
SBA 7(a) acquisition structures.

Usage (CLI):
    python3 scripts/sba_calculator.py --deal deals/aspen-fencing
    python3 scripts/sba_calculator.py --price 1100000 --sde 373919 --rate 10.5

Usage (importable):
    from sba_calculator import sba_feasibility
    result = sba_feasibility(asking_price=1100000, sde=373919, rate_pct=10.5)
"""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from deal_utils import load_deal


def annual_payment(principal, annual_rate_pct, years):
    """Standard amortizing loan annual payment."""
    if principal <= 0:
        return 0
    r = annual_rate_pct / 100
    if r == 0:
        return principal / years
    monthly_rate = r / 12
    n_months = years * 12
    monthly_pmt = principal * (monthly_rate * (1 + monthly_rate) ** n_months) / \
                  ((1 + monthly_rate) ** n_months - 1)
    return round(monthly_pmt * 12)


def sba_feasibility(asking_price, sde, rate_pct=10.5, term_years=10,
                    sba_pct=80, buyer_pct=10, seller_pct=10,
                    seller_rate_pct=6.0, seller_standby_years=2,
                    seller_amort_years=5, min_dscr=1.25,
                    buyer_replacement_costs=0):
    """Compute SBA feasibility for a deal.

    Args:
        asking_price: Total purchase price
        sde: Annual SDE (use weighted average)
        rate_pct: SBA 7(a) interest rate (annual %)
        term_years: SBA loan term in years
        sba_pct: SBA loan as % of price (default 80)
        buyer_pct: Buyer equity as % of price (default 10)
        seller_pct: Seller financing as % of price (default 10)
        seller_rate_pct: Seller note interest rate
        seller_standby_years: Years seller note is on standby (SBA requirement)
        seller_amort_years: Amortization period for seller note after standby
        min_dscr: Minimum acceptable DSCR (SBA standard = 1.25)
        buyer_replacement_costs: Annual costs buyer adds (GM salary, health, etc.)

    Returns:
        dict with all computed values
    """
    sba_loan = round(asking_price * sba_pct / 100)
    buyer_equity = round(asking_price * buyer_pct / 100)
    seller_note = round(asking_price * seller_pct / 100)

    sba_annual = annual_payment(sba_loan, rate_pct, term_years)
    seller_annual = annual_payment(seller_note, seller_rate_pct, seller_amort_years)

    debt_service_standby = sba_annual
    debt_service_full = sba_annual + seller_annual

    effective_sde = sde - buyer_replacement_costs

    dscr_standby = round(effective_sde / debt_service_standby, 2) if debt_service_standby > 0 else 999
    dscr_full = round(effective_sde / debt_service_full, 2) if debt_service_full > 0 else 999

    pass_standby = dscr_standby >= min_dscr
    pass_full = dscr_full >= min_dscr

    # Max supportable price: work backwards from DSCR = min_dscr
    # At min_dscr, max_debt_service = effective_sde / min_dscr
    max_total_ds = effective_sde / min_dscr
    # Approximate: max SBA payment = max_total_ds * (sba_annual / debt_service_full) if both exist
    if debt_service_full > 0 and seller_annual > 0:
        sba_share = sba_annual / debt_service_full
        max_sba_annual = max_total_ds * sba_share
    else:
        max_sba_annual = max_total_ds

    # Reverse the annuity formula to get max principal
    r = rate_pct / 100
    if r > 0:
        monthly_rate = r / 12
        n_months = term_years * 12
        max_sba_monthly = max_sba_annual / 12
        factor = ((1 + monthly_rate) ** n_months - 1) / (monthly_rate * (1 + monthly_rate) ** n_months)
        max_sba_principal = max_sba_monthly * factor
    else:
        max_sba_principal = max_sba_annual * term_years

    max_price = round(max_sba_principal / (sba_pct / 100))

    if pass_full:
        verdict = "FEASIBLE"
    elif pass_standby:
        verdict = "MARGINAL — passes during standby but fails post-standby"
    else:
        verdict = "DOES NOT PENCIL"

    return {
        "asking_price": asking_price,
        "sde_used": sde,
        "buyer_replacement_costs": buyer_replacement_costs,
        "effective_sde": effective_sde,
        "structure": {
            "sba_loan": sba_loan,
            "sba_pct": sba_pct,
            "buyer_equity": buyer_equity,
            "buyer_pct": buyer_pct,
            "seller_note": seller_note,
            "seller_pct": seller_pct,
        },
        "rates": {
            "sba_rate_pct": rate_pct,
            "sba_term_years": term_years,
            "seller_rate_pct": seller_rate_pct,
            "seller_standby_years": seller_standby_years,
            "seller_amort_years": seller_amort_years,
        },
        "debt_service": {
            "sba_annual": sba_annual,
            "seller_annual": seller_annual,
            "total_standby": debt_service_standby,
            "total_post_standby": debt_service_full,
        },
        "dscr": {
            "standby": dscr_standby,
            "post_standby": dscr_full,
            "minimum_required": min_dscr,
            "pass_standby": pass_standby,
            "pass_post_standby": pass_full,
        },
        "max_supportable_price": max_price,
        "verdict": verdict,
    }


def format_report(result):
    """Format a human-readable report."""
    lines = []
    lines.append(f"SBA FEASIBILITY ANALYSIS")
    lines.append(f"{'=' * 50}")
    lines.append(f"")
    lines.append(f"Asking Price:           ${result['asking_price']:>12,.0f}")
    lines.append(f"SDE Used:               ${result['sde_used']:>12,.0f}")
    if result['buyer_replacement_costs'] > 0:
        lines.append(f"Replacement Costs:      ${result['buyer_replacement_costs']:>12,.0f}")
        lines.append(f"Effective SDE:          ${result['effective_sde']:>12,.0f}")
    lines.append(f"")

    s = result['structure']
    lines.append(f"STRUCTURE ({s['sba_pct']}/{s['buyer_pct']}/{s['seller_pct']})")
    lines.append(f"  SBA Loan ({s['sba_pct']}%):        ${s['sba_loan']:>12,.0f}")
    lines.append(f"  Buyer Equity ({s['buyer_pct']}%):    ${s['buyer_equity']:>12,.0f}")
    lines.append(f"  Seller Note ({s['seller_pct']}%):    ${s['seller_note']:>12,.0f}")
    lines.append(f"")

    r = result['rates']
    lines.append(f"RATES")
    lines.append(f"  SBA: {r['sba_rate_pct']}% / {r['sba_term_years']}yr")
    lines.append(f"  Seller: {r['seller_rate_pct']}% / {r['seller_standby_years']}yr standby + {r['seller_amort_years']}yr amort")
    lines.append(f"")

    ds = result['debt_service']
    lines.append(f"DEBT SERVICE")
    lines.append(f"  SBA Annual:           ${ds['sba_annual']:>12,.0f}")
    lines.append(f"  Seller Annual:        ${ds['seller_annual']:>12,.0f}")
    lines.append(f"  Total (standby):      ${ds['total_standby']:>12,.0f}")
    lines.append(f"  Total (post-standby): ${ds['total_post_standby']:>12,.0f}")
    lines.append(f"")

    d = result['dscr']
    def dscr_indicator(val, passing):
        return "PASS" if passing else "FAIL"
    lines.append(f"DSCR (minimum {d['minimum_required']:.2f}x)")
    lines.append(f"  Standby:       {d['standby']:.2f}x  [{dscr_indicator(d['standby'], d['pass_standby'])}]")
    lines.append(f"  Post-standby:  {d['post_standby']:.2f}x  [{dscr_indicator(d['post_standby'], d['pass_post_standby'])}]")
    lines.append(f"")

    lines.append(f"Max Supportable Price:  ${result['max_supportable_price']:>12,.0f}")
    lines.append(f"")
    lines.append(f"VERDICT: {result['verdict']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SBA loan feasibility calculator")
    parser.add_argument("--deal", help="Path to deal folder or deal_state.json")
    parser.add_argument("--price", type=float, help="Asking price (overrides deal state)")
    parser.add_argument("--sde", type=float, help="SDE (overrides deal state)")
    parser.add_argument("--sde-type", choices=["conservative", "moderate"], default="conservative",
                        help="Which SDE to use from deal state (default: conservative)")
    parser.add_argument("--rate", type=float, default=10.5, help="SBA rate %% (default: 10.5)")
    parser.add_argument("--term", type=int, default=10, help="SBA term years (default: 10)")
    parser.add_argument("--replacement", type=float, default=0,
                        help="Annual buyer replacement costs (GM salary, health, etc.)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of report")
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
        print("Error: need --price and --sde, or --deal with populated deal_state.json")
        sys.exit(1)

    result = sba_feasibility(
        asking_price=price,
        sde=sde,
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
