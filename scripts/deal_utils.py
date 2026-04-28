#!/usr/bin/env python3
"""Shared extraction layer for deal_state.json.

Handles schema variations across deals by providing safe accessors
that work regardless of how fields were populated.

Usage:
    from deal_utils import DealState
    ds = DealState("deals/aspen-fencing/deal_state.json")
    rev = ds.revenue_by_year()   # {2023: 1583802, 2024: 1720430, ...}
    sde = ds.sde_reconstructed() # {"conservative": {...}, "moderate": {...}}
"""

import json
import sys
from pathlib import Path


class DealState:
    def __init__(self, path):
        self.path = Path(path)
        with open(self.path) as f:
            self.data = json.load(f)
        self.dims = self.data.get("dimensions", {})

    def _d(self, dim_key):
        return self.dims.get(dim_key, {})

    def _best_value(self, field_entries, prefer_source=None):
        """From a list of multi-source entries, return the highest-confidence value."""
        if not field_entries:
            return None
        if prefer_source:
            for e in field_entries:
                if prefer_source in e.get("source", ""):
                    return e.get("value")
        best = max(field_entries, key=lambda e: e.get("confidence", 0))
        return best.get("value")

    def _yearly_values(self, field_entries, amount_key="amount"):
        """Extract {year: amount} dict from year-keyed field entries."""
        result = {}
        if not field_entries:
            return result
        for entry in field_entries:
            val = entry.get("value", {})
            if isinstance(val, dict) and "year" in val:
                year = int(val["year"])
                amt = val.get(amount_key)
                if amt is not None:
                    if year not in result:
                        result[year] = amt
                    elif entry.get("confidence", 0) > 0.7:
                        result[year] = amt
        return result

    # ── Dimension 1 ──

    def deal_name(self):
        return self.data.get("metadata", {}).get("deal_name", "Unknown")

    def business_name(self):
        entries = self._d("1_business_identity").get("business_name", [])
        return self._best_value(entries) or self.deal_name()

    def entity_type(self):
        entries = self._d("1_business_identity").get("entity_type", [])
        return self._best_value(entries)

    def location(self):
        d1 = self._d("1_business_identity")
        city = self._best_value(d1.get("location_city", []))
        state = self._best_value(d1.get("location_state", []))
        parts = [p for p in [city, state] if p]
        return ", ".join(parts) if parts else None

    # ── Dimension 2 ──

    def asking_price(self):
        entries = self._d("8_deal_economics").get("asking_price", [])
        return self._best_value(entries)

    def revenue_by_year(self):
        entries = self._d("2_financial_performance").get("revenue_by_year", [])
        return self._yearly_values(entries)

    def net_income_by_year(self):
        entries = self._d("2_financial_performance").get("net_income_by_year", [])
        return self._yearly_values(entries)

    def sde_reconstructed(self):
        """Return the sde_reconstructed object if it exists."""
        return self._d("2_financial_performance").get("sde_reconstructed")

    def sde_conservative_by_year(self):
        sde = self.sde_reconstructed()
        if not sde:
            return {}
        by_year = sde.get("conservative", {}).get("by_year", {})
        return {int(k): v for k, v in by_year.items()}

    def sde_moderate_by_year(self):
        sde = self.sde_reconstructed()
        if not sde:
            return {}
        by_year = sde.get("moderate", {}).get("by_year", {})
        return {int(k): v for k, v in by_year.items()}

    def sde_conservative_weighted(self):
        sde = self.sde_reconstructed()
        if not sde:
            return None
        return sde.get("conservative", {}).get("weighted_avg_1_2_3")

    def sde_moderate_weighted(self):
        sde = self.sde_reconstructed()
        if not sde:
            return None
        return sde.get("moderate", {}).get("weighted_avg_1_2_3")

    # ── Dimension 8 ──

    def valuation_lender(self):
        return self._d("8_deal_economics").get("valuation_lender_view")

    def valuation_cpa(self):
        return self._d("8_deal_economics").get("valuation_cpa_view")

    def valuation_buyer(self):
        return self._d("8_deal_economics").get("valuation_buyer_view")

    def sba_feasibility(self):
        return self._d("8_deal_economics").get("sba_loan_feasibility")

    # ── Utility ──

    def weighted_average(self, yearly_dict, weights=None):
        """Compute weighted average from {year: value} dict.
        Default weights: 1x oldest, 2x middle, 3x newest."""
        if not yearly_dict:
            return None
        years = sorted(yearly_dict.keys())
        if weights is None:
            weights = list(range(1, len(years) + 1))
        if len(weights) != len(years):
            weights = list(range(1, len(years) + 1))
        total = sum(yearly_dict[y] * w for y, w in zip(years, weights))
        return round(total / sum(weights))

    def years_available(self):
        """Return sorted list of years with financial data."""
        rev = self.revenue_by_year()
        ni = self.net_income_by_year()
        return sorted(set(rev.keys()) | set(ni.keys()))


def load_deal(deal_path):
    """Convenience: load a DealState from a deal folder or deal_state.json path."""
    p = Path(deal_path)
    if p.is_dir():
        p = p / "deal_state.json"
    return DealState(p)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 deal_utils.py <deal_state.json or deal folder>")
        sys.exit(1)
    ds = load_deal(sys.argv[1])
    print(f"Deal: {ds.deal_name()}")
    print(f"Business: {ds.business_name()}")
    print(f"Location: {ds.location()}")
    print(f"Asking: ${ds.asking_price():,.0f}" if ds.asking_price() else "Asking: N/A")
    print(f"Revenue: {ds.revenue_by_year()}")
    print(f"Net Income: {ds.net_income_by_year()}")
    print(f"Conservative SDE: {ds.sde_conservative_by_year()}")
    print(f"Moderate SDE: {ds.sde_moderate_by_year()}")
    print(f"Years: {ds.years_available()}")
