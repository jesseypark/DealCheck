#!/usr/bin/env python3
"""Generate a P&L + SDE + DSCR workbook for Number One Home Care Agency.

Produces a multi-sheet .xlsx with:
  Sheet 1 — P&L with all line items across 2023/2024/2025/TTM, add-backs, SDE walkdown
  Sheet 2 — Deal Economics: financing inputs, deal costs, DSCR calculations, cash-to-close
  Sheet 3 — DSCR Sensitivity matrix (interest rate x purchase price)

All calculation cells use live Excel formulas.
"""

import argparse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter


# ── Styling ──────────────────────────────────────────────────────────────────

HEADER_FONT = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F5233", end_color="2F5233", fill_type="solid")
SECTION_FONT = Font(name="Calibri", bold=True, size=11)
SECTION_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
INPUT_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
TOTAL_FONT = Font(name="Calibri", bold=True, size=11)
TOTAL_FILL = PatternFill(start_color="D6E4C8", end_color="D6E4C8", fill_type="solid")
SDE_FONT = Font(name="Calibri", bold=True, size=12)
SDE_FILL = PatternFill(start_color="2F5233", end_color="2F5233", fill_type="solid")
SDE_FONT_WHITE = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
PASS_FONT = Font(name="Calibri", bold=True, color="006100")
FAIL_FONT = Font(name="Calibri", bold=True, color="9C0006")
PASS_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
FAIL_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
THIN_BORDER = Border(
    bottom=Side(style="thin", color="CCCCCC"),
)
THICK_BORDER_TOP = Border(
    top=Side(style="medium", color="2F5233"),
    bottom=Side(style="medium", color="2F5233"),
)
ACCT_FMT = '#,##0'
ACCT_FMT_NEG = '#,##0;[Red](#,##0)'
PCT_FMT = '0.0%'
DSCR_FMT = '0.00"x"'
DOLLAR_FMT = '$#,##0'


def style_header_row(ws, row, max_col):
    for c in range(1, max_col + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", wrap_text=True)


def style_section_row(ws, row, max_col):
    for c in range(1, max_col + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = SECTION_FONT
        cell.fill = SECTION_FILL


def style_total_row(ws, row, max_col):
    for c in range(1, max_col + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = TOTAL_FONT
        cell.fill = TOTAL_FILL
        cell.border = THICK_BORDER_TOP


def style_sde_row(ws, row, max_col):
    for c in range(1, max_col + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = SDE_FONT_WHITE
        cell.fill = SDE_FILL
        cell.border = THICK_BORDER_TOP


def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write_input_cell(ws, row, col, value, fmt=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = INPUT_FILL
    if fmt:
        cell.number_format = fmt
    return cell


# ── P&L Data ─────────────────────────────────────────────────────────────────
# Line items from CIM recast pages (pages 14-17).
# Master list is the union of all line items across all 4 years.
# Values are from the Seller's Statements column (pre-adjustment).

LINE_ITEMS = [
    # (label, 2023, 2024, 2025, TTM)
    ("Advertising", 884, 524, 78, 168),
    ("Background Checks", 532, 0, 0, 941),
    ("Bank Charges", 172, 429, 218, 126),
    ("Business Licenses", 2393, 1633, 1652, 0),
    ("Colorado Tax", 0, 0, 0, 867),
    ("Continuing Education", 3838, 0, 0, 3970),
    ("Contractor", 0, 1411, 300, 0),
    ("Employee Advances", 0, 0, 0, 1600),
    ("Employee Expenses", 0, 1492, 6316, 0),
    ("Employee Gifts / Gifts to Employees", 2250, 0, 0, 3250),
    ("Insurance - Business", 30727, 36703, 50759, 23975),
    ("Insurance - Workers Comp", 0, 0, 0, 18807),
    ("Interest", 0, 514, 147, 0),
    ("Legal and Professional", 7311, 10849, 25899, 42238),
    ("Licenses & Permits", 0, 0, 0, 1606),
    ("Meals & Entertainment", 122, 0, 0, 0),
    ("Miscellaneous", 0, 1001, 431, 0),
    ("Office Expenses", 4967, 8671, 11613, 6509),
    ("Office Supplies", 0, 0, 0, 4690),
    ("Payroll - Employees", 1563312, 1942664, 2634101, 2683832),
    ("Payroll - Officers", 216000, 216000, 246714, 198000),
    ("Payroll Costs / Services", 2373, 2632, 0, 3983),
    ("Payroll Expenses - Company Contributions", 0, 0, 0, 2922),
    ("Payroll Taxes / Taxes and Licenses", 188807, 235116, 253858, 270234),
    ("Postage", 779, 603, 1207, 1315),
    ("Recruiting Expense", 0, 0, 0, 12),
    ("Reimbursement", 0, 0, 0, 89),
    ("Rent", 11045, 14340, 26729, 20213),
    ("Repairs", 0, 216, 0, 0),
    ("Services", 1818, 0, 0, 0),
    ("Staples", 0, 0, 0, 48),
    ("Telephone", 6399, 6719, 1571, 3445),
    ("Travel", 646, 0, 31, 15),
    ("Utilities", 0, 0, 10, 10),
]

# Add-back items per year (label, 2023, 2024, 2025, TTM, reason)
ADD_BACKS = [
    ("Officers Compensation", 216000, 216000, 246714, 198000, "Owner salary — always add back"),
    ("Owner Payroll Taxes", 15041, 17289, 19754, 17400, "Employer taxes on owner comp"),
    ("Interest", 0, 514, 147, 0, "Always add back"),
    ("Meals & Entertainment", 122, 0, 0, 0, "Owner discretion"),
]

# Verified summary numbers from financial analyst report
REVENUE = {"2023": 2275090, "2024": 3040911, "2025": 3965105, "TTM": 4352972}
NET_INCOME = {"2023": 231755, "2024": 560813, "2025": 631286, "TTM": 1061478}
TOTAL_ADDBACKS = {"2023": 231163, "2024": 233603, "2025": 266615, "TTM": 215400}
SDE = {"2023": 462918, "2024": 794247, "2025": 897941, "TTM": 1276878}


def build_pnl_sheet(wb):
    ws = wb.active
    ws.title = "P&L + SDE"
    ws.sheet_properties.tabColor = "2F5233"

    periods = ["2023", "2024", "2025", "TTM"]
    set_col_widths(ws, [42, 16, 16, 16, 16, 3, 16, 16])

    # Columns: A=label, B=2023, C=2024, D=2025, E=TTM, F=spacer, G=YoY%(latest), H=notes
    row = 1
    ws.cell(row=row, column=1, value="Number One Home Care Agency")
    ws.cell(row=row, column=1).font = Font(name="Calibri", bold=True, size=14)
    row = 2
    ws.cell(row=row, column=1, value="P&L Recast + SDE Reconstruction — CIM Basis (Confidence 0.50)")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=10, color="666666")

    row = 4
    headers = ["", "2023", "2024", "2025", "TTM (Apr 2026)", "", "YoY %\n(2025→TTM)"]
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header_row(ws, row, 7)

    # ── Revenue section ──
    row = 5
    ws.cell(row=row, column=1, value="REVENUE")
    style_section_row(ws, row, 7)

    row = 6
    ws.cell(row=row, column=1, value="Gross Sales")
    rev_row = row
    for c, p in enumerate(periods, 2):
        cell = ws.cell(row=row, column=c, value=REVENUE[p])
        cell.number_format = ACCT_FMT
    # YoY formula
    ws.cell(row=row, column=7).value = f"=(E{row}-D{row})/D{row}"
    ws.cell(row=row, column=7).number_format = PCT_FMT

    row = 7
    ws.cell(row=row, column=1, value="Cost of Goods Sold")
    for c in range(2, 6):
        ws.cell(row=row, column=c, value=0)
        ws.cell(row=row, column=c).number_format = ACCT_FMT
    cogs_row = row

    row = 8
    ws.cell(row=row, column=1, value="GROSS PROFIT")
    gp_row = row
    for c in range(2, 6):
        ws.cell(row=row, column=c).value = f"={get_column_letter(c)}{rev_row}-{get_column_letter(c)}{cogs_row}"
        ws.cell(row=row, column=c).number_format = ACCT_FMT
    style_total_row(ws, row, 7)

    # ── Expenses section ──
    row = 10
    ws.cell(row=row, column=1, value="OPERATING EXPENSES")
    style_section_row(ws, row, 7)

    expense_start_row = row + 1
    for i, (label, v2023, v2024, v2025, vttm) in enumerate(LINE_ITEMS):
        r = expense_start_row + i
        ws.cell(row=r, column=1, value=label)
        for c, val in zip(range(2, 6), [v2023, v2024, v2025, vttm]):
            cell = ws.cell(row=r, column=c, value=val)
            cell.number_format = ACCT_FMT
        ws.cell(row=r, column=1).border = THIN_BORDER
        for c in range(2, 6):
            ws.cell(row=r, column=c).border = THIN_BORDER
        # YoY for significant items
        if v2025 > 0 and vttm > 0:
            ws.cell(row=r, column=7).value = f"=(E{r}-D{r})/D{r}"
            ws.cell(row=r, column=7).number_format = PCT_FMT

    expense_end_row = expense_start_row + len(LINE_ITEMS) - 1

    # Total Expenses
    row = expense_end_row + 1
    ws.cell(row=row, column=1, value="TOTAL EXPENSES")
    total_exp_row = row
    for c in range(2, 6):
        col_letter = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"=SUM({col_letter}{expense_start_row}:{col_letter}{expense_end_row})"
        ws.cell(row=row, column=c).number_format = ACCT_FMT
    style_total_row(ws, row, 7)

    # ── Net Income ──
    row = total_exp_row + 2
    ws.cell(row=row, column=1, value="NET INCOME (before adjustments)")
    ni_row = row
    for c in range(2, 6):
        col_letter = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"={col_letter}{gp_row}-{col_letter}{total_exp_row}"
        ws.cell(row=row, column=c).number_format = ACCT_FMT
    style_total_row(ws, row, 7)
    ws.cell(row=row, column=7).value = f"=(E{row}-D{row})/D{row}"
    ws.cell(row=row, column=7).number_format = PCT_FMT

    # ── Verified Net Income row (for cross-check) ──
    row = ni_row + 1
    ws.cell(row=row, column=1, value="  (Broker stated Net Income)")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=9, color="888888")
    for c, p in enumerate(periods, 2):
        cell = ws.cell(row=row, column=c, value=NET_INCOME[p])
        cell.number_format = ACCT_FMT
        cell.font = Font(name="Calibri", italic=True, size=9, color="888888")

    # ── Add-Backs section ──
    row = ni_row + 3
    ws.cell(row=row, column=1, value="SDE ADD-BACKS")
    style_section_row(ws, row, 7)
    addback_header_row = row

    row += 1
    headers2 = ["", "2023", "2024", "2025", "TTM (Apr 2026)", "", "Classification"]
    for c, h in enumerate(headers2, 1):
        ws.cell(row=row, column=c, value=h)
    style_header_row(ws, row, 7)

    addback_start_row = row + 1
    for i, (label, v2023, v2024, v2025, vttm, reason) in enumerate(ADD_BACKS):
        r = addback_start_row + i
        ws.cell(row=r, column=1, value=label)
        for c, val in zip(range(2, 6), [v2023, v2024, v2025, vttm]):
            cell = ws.cell(row=r, column=c, value=val)
            cell.number_format = ACCT_FMT
        ws.cell(row=r, column=7, value=reason)
        ws.cell(row=r, column=7).font = Font(name="Calibri", size=9, color="666666")
        for c in range(1, 8):
            ws.cell(row=r, column=c).border = THIN_BORDER

    addback_end_row = addback_start_row + len(ADD_BACKS) - 1

    # Total Add-Backs
    row = addback_end_row + 1
    ws.cell(row=row, column=1, value="TOTAL ADD-BACKS")
    total_ab_row = row
    for c in range(2, 6):
        col_letter = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"=SUM({col_letter}{addback_start_row}:{col_letter}{addback_end_row})"
        ws.cell(row=row, column=c).number_format = ACCT_FMT
    style_total_row(ws, row, 7)

    # ── SDE ──
    row = total_ab_row + 2
    ws.cell(row=row, column=1, value="SELLER'S DISCRETIONARY EARNINGS (SDE)")
    sde_row = row
    for c in range(2, 6):
        col_letter = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"={col_letter}{ni_row}+{col_letter}{total_ab_row}"
        ws.cell(row=row, column=c).number_format = ACCT_FMT
    style_sde_row(ws, row, 7)
    ws.cell(row=row, column=7).value = f"=(E{row}-D{row})/D{row}"
    ws.cell(row=row, column=7).number_format = PCT_FMT
    ws.cell(row=row, column=7).font = SDE_FONT_WHITE

    # SDE Margin
    row = sde_row + 1
    ws.cell(row=row, column=1, value="SDE Margin")
    for c in range(2, 6):
        col_letter = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"={col_letter}{sde_row}/{col_letter}{rev_row}"
        ws.cell(row=row, column=c).number_format = PCT_FMT
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True)

    # Broker SDE cross-check
    row = sde_row + 2
    ws.cell(row=row, column=1, value="  (Broker stated SDE)")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=9, color="888888")
    for c, p in enumerate(periods, 2):
        cell = ws.cell(row=row, column=c, value=SDE[p])
        cell.number_format = ACCT_FMT
        cell.font = Font(name="Calibri", italic=True, size=9, color="888888")

    # ── Key Metrics ──
    row = sde_row + 4
    ws.cell(row=row, column=1, value="KEY METRICS")
    style_section_row(ws, row, 7)

    row += 1
    ws.cell(row=row, column=1, value="Revenue Growth (YoY)")
    ws.cell(row=row, column=2).value = "—"
    for c in range(3, 6):
        prev = get_column_letter(c - 1)
        cur = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"=({cur}{rev_row}-{prev}{rev_row})/{prev}{rev_row}"
        ws.cell(row=row, column=c).number_format = PCT_FMT

    row += 1
    ws.cell(row=row, column=1, value="Payroll Employees as % of Revenue")
    payroll_emp_offset = None
    for i, (label, *_) in enumerate(LINE_ITEMS):
        if label == "Payroll - Employees":
            payroll_emp_offset = i
            break
    if payroll_emp_offset is not None:
        pe_row = expense_start_row + payroll_emp_offset
        for c in range(2, 6):
            col_letter = get_column_letter(c)
            ws.cell(row=row, column=c).value = f"={col_letter}{pe_row}/{col_letter}{rev_row}"
            ws.cell(row=row, column=c).number_format = PCT_FMT

    row += 1
    ws.cell(row=row, column=1, value="Officer Comp as % of Revenue")
    po_offset = None
    for i, (label, *_) in enumerate(LINE_ITEMS):
        if label == "Payroll - Officers":
            po_offset = i
            break
    if po_offset is not None:
        po_row = expense_start_row + po_offset
        for c in range(2, 6):
            col_letter = get_column_letter(c)
            ws.cell(row=row, column=c).value = f"={col_letter}{po_row}/{col_letter}{rev_row}"
            ws.cell(row=row, column=c).number_format = PCT_FMT

    row += 1
    ws.cell(row=row, column=1, value="SDE Growth (YoY)")
    ws.cell(row=row, column=2).value = "—"
    for c in range(3, 6):
        prev = get_column_letter(c - 1)
        cur = get_column_letter(c)
        ws.cell(row=row, column=c).value = f"=({cur}{sde_row}-{prev}{sde_row})/{prev}{sde_row}"
        ws.cell(row=row, column=c).number_format = PCT_FMT

    # Freeze panes
    ws.freeze_panes = "B5"

    return {
        "sde_row": sde_row,
        "rev_row": rev_row,
        "ni_row": ni_row,
    }


def build_deal_economics_sheet(wb, pnl_refs):
    ws = wb.create_sheet("Deal Economics")
    ws.sheet_properties.tabColor = "1F4E79"

    set_col_widths(ws, [36, 18, 5, 36, 18])

    sde_row = pnl_refs["sde_row"]

    row = 1
    ws.cell(row=row, column=1, value="DEAL ECONOMICS & DSCR CALCULATOR")
    ws.cell(row=row, column=1).font = Font(name="Calibri", bold=True, size=14)
    row = 2
    ws.cell(row=row, column=1, value="Yellow cells are editable inputs — change them to model scenarios")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=10, color="666666")

    # ── Purchase & SDE Inputs ──
    row = 4
    ws.cell(row=row, column=1, value="PURCHASE & SDE")
    style_section_row(ws, row, 5)

    row = 5
    ws.cell(row=row, column=1, value="Purchase Price")
    price_row = row
    write_input_cell(ws, row, 2, 5500000, DOLLAR_FMT)

    row = 6
    ws.cell(row=row, column=1, value="SDE (from P&L sheet, TTM)")
    sde_ref_row = row
    ws.cell(row=row, column=2).value = f"='P&L + SDE'!E{sde_row}"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    row = 7
    ws.cell(row=row, column=1, value="SDE Override (leave blank to use above)")
    sde_override_row = row
    write_input_cell(ws, row, 2, None, DOLLAR_FMT)

    row = 8
    ws.cell(row=row, column=1, value="SDE Used in Calculations")
    sde_used_row = row
    ws.cell(row=row, column=2).value = f'=IF(B{sde_override_row}<>"",B{sde_override_row},B{sde_ref_row})'
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    ws.cell(row=row, column=2).font = TOTAL_FONT

    row = 9
    ws.cell(row=row, column=1, value="Owner Replacement Cost (annual)")
    replacement_row = row
    write_input_cell(ws, row, 2, 87000, DOLLAR_FMT)

    row = 10
    ws.cell(row=row, column=1, value="Effective SDE (SDE - Replacement)")
    effective_sde_row = row
    ws.cell(row=row, column=2).value = f"=B{sde_used_row}-B{replacement_row}"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    ws.cell(row=row, column=2).font = TOTAL_FONT

    row = 11
    ws.cell(row=row, column=1, value="Asking Price Multiple (on SDE)")
    ws.cell(row=row, column=2).value = f"=B{price_row}/B{sde_used_row}"
    ws.cell(row=row, column=2).number_format = '0.00"x"'

    # ── Financing Structure ──
    row = 13
    ws.cell(row=row, column=1, value="FINANCING STRUCTURE")
    style_section_row(ws, row, 5)

    row = 14
    ws.cell(row=row, column=1, value="SBA Loan %")
    sba_pct_row = row
    write_input_cell(ws, row, 2, 0.80, PCT_FMT)

    row = 15
    ws.cell(row=row, column=1, value="Buyer Equity %")
    buyer_pct_row = row
    write_input_cell(ws, row, 2, 0.10, PCT_FMT)

    row = 16
    ws.cell(row=row, column=1, value="Seller Note %")
    seller_pct_row = row
    write_input_cell(ws, row, 2, 0.10, PCT_FMT)

    row = 17
    ws.cell(row=row, column=1, value="  Check (must = 100%)")
    ws.cell(row=row, column=2).value = f"=B{sba_pct_row}+B{buyer_pct_row}+B{seller_pct_row}"
    ws.cell(row=row, column=2).number_format = PCT_FMT
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=9, color="888888")

    row = 19
    ws.cell(row=row, column=1, value="SBA Loan Amount")
    sba_loan_row = row
    ws.cell(row=row, column=2).value = f"=ROUND(B{price_row}*B{sba_pct_row},0)"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    row = 20
    ws.cell(row=row, column=1, value="Buyer Equity Amount")
    buyer_eq_row = row
    ws.cell(row=row, column=2).value = f"=ROUND(B{price_row}*B{buyer_pct_row},0)"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    row = 21
    ws.cell(row=row, column=1, value="Seller Note Amount")
    seller_note_row = row
    ws.cell(row=row, column=2).value = f"=ROUND(B{price_row}*B{seller_pct_row},0)"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    # ── Loan Terms ──
    row = 23
    ws.cell(row=row, column=1, value="LOAN TERMS")
    style_section_row(ws, row, 5)

    row = 24
    ws.cell(row=row, column=1, value="SBA Interest Rate (annual)")
    sba_rate_row = row
    write_input_cell(ws, row, 2, 0.105, PCT_FMT)

    row = 25
    ws.cell(row=row, column=1, value="SBA Loan Term (years)")
    sba_term_row = row
    write_input_cell(ws, row, 2, 10, ACCT_FMT)

    row = 26
    ws.cell(row=row, column=1, value="Seller Note Interest Rate")
    seller_rate_row = row
    write_input_cell(ws, row, 2, 0.06, PCT_FMT)

    row = 27
    ws.cell(row=row, column=1, value="Seller Note Amortization (years)")
    seller_amort_row = row
    write_input_cell(ws, row, 2, 5, ACCT_FMT)

    row = 28
    ws.cell(row=row, column=1, value="Seller Note Standby Period (years)")
    seller_standby_row = row
    write_input_cell(ws, row, 2, 2, ACCT_FMT)

    # ── Debt Service Calculations ──
    row = 30
    ws.cell(row=row, column=1, value="DEBT SERVICE")
    style_section_row(ws, row, 5)

    row = 31
    ws.cell(row=row, column=1, value="SBA Monthly Payment")
    sba_monthly_row = row
    ws.cell(row=row, column=2).value = (
        f"=IF(B{sba_rate_row}=0, B{sba_loan_row}/(B{sba_term_row}*12), "
        f"-PMT(B{sba_rate_row}/12, B{sba_term_row}*12, B{sba_loan_row}))"
    )
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    row = 32
    ws.cell(row=row, column=1, value="SBA Annual Debt Service")
    sba_annual_row = row
    ws.cell(row=row, column=2).value = f"=B{sba_monthly_row}*12"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    ws.cell(row=row, column=2).font = TOTAL_FONT

    row = 33
    ws.cell(row=row, column=1, value="Seller Note Monthly Payment")
    seller_monthly_row = row
    ws.cell(row=row, column=2).value = (
        f"=IF(B{seller_rate_row}=0, B{seller_note_row}/(B{seller_amort_row}*12), "
        f"-PMT(B{seller_rate_row}/12, B{seller_amort_row}*12, B{seller_note_row}))"
    )
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    row = 34
    ws.cell(row=row, column=1, value="Seller Note Annual Debt Service")
    seller_annual_row = row
    ws.cell(row=row, column=2).value = f"=B{seller_monthly_row}*12"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    ws.cell(row=row, column=2).font = TOTAL_FONT

    row = 36
    ws.cell(row=row, column=1, value="Total Debt Service (Standby — SBA only)")
    ds_standby_row = row
    ws.cell(row=row, column=2).value = f"=B{sba_annual_row}"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    style_total_row(ws, row, 2)

    row = 37
    ws.cell(row=row, column=1, value="Total Debt Service (Post-Standby — SBA + Seller)")
    ds_full_row = row
    ws.cell(row=row, column=2).value = f"=B{sba_annual_row}+B{seller_annual_row}"
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    style_total_row(ws, row, 2)

    # ── DSCR ──
    row = 39
    ws.cell(row=row, column=1, value="DSCR ANALYSIS")
    style_section_row(ws, row, 5)

    row = 40
    ws.cell(row=row, column=1, value="Minimum Required DSCR")
    min_dscr_row = row
    write_input_cell(ws, row, 2, 1.25, DSCR_FMT)

    row = 42
    ws.cell(row=row, column=1, value="DSCR (Standby Period)")
    dscr_standby_row = row
    ws.cell(row=row, column=2).value = f"=B{effective_sde_row}/B{ds_standby_row}"
    ws.cell(row=row, column=2).number_format = DSCR_FMT
    ws.cell(row=row, column=2).font = TOTAL_FONT

    row = 43
    ws.cell(row=row, column=1, value="  Pass/Fail")
    dscr_standby_pf_row = row
    ws.cell(row=row, column=2).value = f'=IF(B{dscr_standby_row}>=B{min_dscr_row},"PASS","FAIL")'

    row = 45
    ws.cell(row=row, column=1, value="DSCR (Post-Standby)")
    dscr_full_row = row
    ws.cell(row=row, column=2).value = f"=B{effective_sde_row}/B{ds_full_row}"
    ws.cell(row=row, column=2).number_format = DSCR_FMT
    ws.cell(row=row, column=2).font = TOTAL_FONT

    row = 46
    ws.cell(row=row, column=1, value="  Pass/Fail")
    dscr_full_pf_row = row
    ws.cell(row=row, column=2).value = f'=IF(B{dscr_full_row}>=B{min_dscr_row},"PASS","FAIL")'

    row = 48
    ws.cell(row=row, column=1, value="VERDICT")
    verdict_row = row
    ws.cell(row=row, column=2).value = (
        f'=IF(B{dscr_full_row}>=B{min_dscr_row},"FEASIBLE",'
        f'IF(B{dscr_standby_row}>=B{min_dscr_row},"MARGINAL — standby only","DOES NOT PENCIL"))'
    )
    ws.cell(row=row, column=2).font = Font(name="Calibri", bold=True, size=12)

    # ── Deal Costs (right side) ──
    col_d = 4
    cost_row_start = 4
    ws.cell(row=cost_row_start, column=col_d, value="DEAL COSTS & CASH TO CLOSE")
    style_section_row(ws, cost_row_start, 5)
    # Only style cols D-E
    for c in [4, 5]:
        ws.cell(row=cost_row_start, column=c).font = SECTION_FONT
        ws.cell(row=cost_row_start, column=c).fill = SECTION_FILL

    costs = [
        ("Attorney / Legal", 15000),
        ("Quality of Earnings (QofE)", 20000),
        ("Accounting / Tax Advisory", 5000),
        ("Business Valuation", 5000),
        ("SBA Guarantee Fee (approx 3%)", None),  # formula
        ("Environmental / Inspection", 0),
        ("Franchise Transfer Fee", 0),
        ("Other Closing Costs", 0),
    ]

    cost_rows = {}
    r = cost_row_start + 1
    for label, val in costs:
        ws.cell(row=r, column=col_d, value=label)
        if label.startswith("SBA Guarantee"):
            sba_fee_row = r
            ws.cell(row=r, column=col_d + 1).value = f"=ROUND(B{sba_loan_row}*0.03,0)"
            ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT
        else:
            write_input_cell(ws, r, col_d + 1, val, DOLLAR_FMT)
        cost_rows[label] = r
        ws.cell(row=r, column=col_d).border = THIN_BORDER
        ws.cell(row=r, column=col_d + 1).border = THIN_BORDER
        r += 1

    total_costs_row = r
    ws.cell(row=r, column=col_d, value="TOTAL DEAL COSTS")
    ws.cell(row=r, column=col_d).font = TOTAL_FONT
    col_e = get_column_letter(col_d + 1)
    ws.cell(row=r, column=col_d + 1).value = f"=SUM({col_e}{cost_row_start+1}:{col_e}{r-1})"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT
    ws.cell(row=r, column=col_d + 1).font = TOTAL_FONT
    style_total_row(ws, r, 5)

    # ROBS section
    r += 2
    ws.cell(row=r, column=col_d, value="ROBS (if applicable)")
    for c in [col_d, col_d + 1]:
        ws.cell(row=r, column=c).font = SECTION_FONT
        ws.cell(row=r, column=c).fill = SECTION_FILL

    r += 1
    ws.cell(row=r, column=col_d, value="ROBS Setup Cost")
    robs_setup_row = r
    write_input_cell(ws, r, col_d + 1, 0, DOLLAR_FMT)

    r += 1
    ws.cell(row=r, column=col_d, value="ROBS Annual Ongoing Cost")
    robs_annual_row = r
    write_input_cell(ws, r, col_d + 1, 0, DOLLAR_FMT)

    r += 1
    ws.cell(row=r, column=col_d, value="ROBS 401(k) Amount Used")
    robs_amount_row = r
    write_input_cell(ws, r, col_d + 1, 0, DOLLAR_FMT)

    # Working capital
    r += 2
    ws.cell(row=r, column=col_d, value="WORKING CAPITAL RESERVE")
    for c in [col_d, col_d + 1]:
        ws.cell(row=r, column=c).font = SECTION_FONT
        ws.cell(row=r, column=c).fill = SECTION_FILL

    r += 1
    ws.cell(row=r, column=col_d, value="Working Capital / Cash Reserve")
    wc_row = r
    write_input_cell(ws, r, col_d + 1, 50000, DOLLAR_FMT)

    # Cash to close summary
    r += 2
    ws.cell(row=r, column=col_d, value="TOTAL CASH TO CLOSE")
    for c in [col_d, col_d + 1]:
        ws.cell(row=r, column=c).font = SECTION_FONT
        ws.cell(row=r, column=c).fill = SECTION_FILL
    cash_close_header = r

    r += 1
    ws.cell(row=r, column=col_d, value="Buyer Equity (down payment)")
    ws.cell(row=r, column=col_d + 1).value = f"=B{buyer_eq_row}"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT

    r += 1
    ws.cell(row=r, column=col_d, value="Deal Costs")
    ws.cell(row=r, column=col_d + 1).value = f"={col_e}{total_costs_row}"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT

    r += 1
    ws.cell(row=r, column=col_d, value="ROBS Setup")
    ws.cell(row=r, column=col_d + 1).value = f"={col_e}{robs_setup_row}"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT

    r += 1
    ws.cell(row=r, column=col_d, value="Working Capital Reserve")
    ws.cell(row=r, column=col_d + 1).value = f"={col_e}{wc_row}"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT

    r += 1
    ws.cell(row=r, column=col_d, value="TOTAL CASH NEEDED")
    total_cash_row = r
    ws.cell(row=r, column=col_d + 1).value = f"=SUM({col_e}{cash_close_header+1}:{col_e}{r-1})"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT
    ws.cell(row=r, column=col_d + 1).font = TOTAL_FONT
    style_total_row(ws, r, 5)

    r += 1
    ws.cell(row=r, column=col_d, value="Less: ROBS 401(k) Funds")
    ws.cell(row=r, column=col_d + 1).value = f"={col_e}{robs_amount_row}"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT

    r += 1
    ws.cell(row=r, column=col_d, value="NET OUT-OF-POCKET CASH")
    ws.cell(row=r, column=col_d + 1).value = f"={col_e}{total_cash_row}-{col_e}{r-1}"
    ws.cell(row=r, column=col_d + 1).number_format = DOLLAR_FMT
    ws.cell(row=r, column=col_d + 1).font = Font(name="Calibri", bold=True, size=12)
    style_total_row(ws, r, 5)

    ws.freeze_panes = "A1"

    return {
        "price_row": price_row,
        "sde_used_row": sde_used_row,
        "effective_sde_row": effective_sde_row,
        "sba_rate_row": sba_rate_row,
        "sba_term_row": sba_term_row,
        "sba_pct_row": sba_pct_row,
        "sba_loan_row": sba_loan_row,
        "seller_rate_row": seller_rate_row,
        "seller_amort_row": seller_amort_row,
        "seller_note_row": seller_note_row,
        "ds_standby_row": ds_standby_row,
        "ds_full_row": ds_full_row,
        "min_dscr_row": min_dscr_row,
        "replacement_row": replacement_row,
    }


def build_sensitivity_sheet(wb, econ_refs):
    ws = wb.create_sheet("DSCR Sensitivity")
    ws.sheet_properties.tabColor = "C00000"

    set_col_widths(ws, [24, 14, 14, 14, 14, 14, 14])

    row = 1
    ws.cell(row=row, column=1, value="DSCR SENSITIVITY MATRIX")
    ws.cell(row=row, column=1).font = Font(name="Calibri", bold=True, size=14)
    row = 2
    ws.cell(row=row, column=1, value="Post-standby DSCR across interest rates and purchase prices")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=10, color="666666")
    row = 3
    ws.cell(row=row, column=1, value="Green = PASS (>=1.25x), Red = FAIL")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=10, color="666666")

    # References back to Deal Economics sheet
    de = "'Deal Economics'"
    price_ref = f"{de}!B{econ_refs['price_row']}"
    sde_ref = f"{de}!B{econ_refs['sde_used_row']}"
    eff_sde_ref = f"{de}!B{econ_refs['effective_sde_row']}"
    sba_pct_ref = f"{de}!B{econ_refs['sba_pct_row']}"
    sba_term_ref = f"{de}!B{econ_refs['sba_term_row']}"
    seller_rate_ref = f"{de}!B{econ_refs['seller_rate_row']}"
    seller_amort_ref = f"{de}!B{econ_refs['seller_amort_row']}"
    seller_pct_ref = f"(1-{sba_pct_ref}-{de}!B{econ_refs['replacement_row']-5})"
    replacement_ref = f"{de}!B{econ_refs['replacement_row']}"

    # Price variations: -20%, -10%, base, +10%, +20%
    price_pcts = [-0.20, -0.10, 0, 0.10, 0.20]
    # Interest rate variations
    rates = [0.085, 0.09, 0.095, 0.10, 0.105, 0.11, 0.115]

    # Header row
    row = 5
    ws.cell(row=row, column=1, value="Rate ↓  /  Price →")
    ws.cell(row=row, column=1).font = HEADER_FONT
    ws.cell(row=row, column=1).fill = HEADER_FILL

    for j, pct in enumerate(price_pcts):
        c = j + 2
        if pct == 0:
            label = f"Base Price"
        else:
            label = f"{pct:+.0%}"
        ws.cell(row=row, column=c, value=label)
        ws.cell(row=row, column=c).font = HEADER_FONT
        ws.cell(row=row, column=c).fill = HEADER_FILL
        ws.cell(row=row, column=c).alignment = Alignment(horizontal="center")

    # Price value row
    row = 6
    ws.cell(row=row, column=1, value="Purchase Price")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=9)
    for j, pct in enumerate(price_pcts):
        c = j + 2
        ws.cell(row=row, column=c).value = f"={price_ref}*(1+{pct})"
        ws.cell(row=row, column=c).number_format = '$#,##0'
        ws.cell(row=row, column=c).font = Font(name="Calibri", italic=True, size=9)
        ws.cell(row=row, column=c).alignment = Alignment(horizontal="center")

    # DSCR matrix
    for i, rate in enumerate(rates):
        r = 7 + i
        ws.cell(row=r, column=1, value=rate)
        ws.cell(row=r, column=1).number_format = '0.0%'
        ws.cell(row=r, column=1).font = Font(name="Calibri", bold=True)

        for j, pct in enumerate(price_pcts):
            c = j + 2
            price_formula = f"{price_ref}*(1+{pct})"
            sba_loan = f"ROUND({price_formula}*{sba_pct_ref},0)"
            seller_note = f"ROUND({price_formula}*0.1,0)"

            sba_pmt = f"(-PMT({rate}/12,{sba_term_ref}*12,{sba_loan})*12)"
            seller_pmt = f"(-PMT({seller_rate_ref}/12,{seller_amort_ref}*12,{seller_note})*12)"

            formula = f"={eff_sde_ref}/({sba_pmt}+{seller_pmt})"
            ws.cell(row=r, column=c).value = formula
            ws.cell(row=r, column=c).number_format = DSCR_FMT
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center")

    # Conditional formatting via formulas (manual style since openpyxl CF is limited for this)
    # We'll add a note instead
    row = 7 + len(rates) + 1
    ws.cell(row=row, column=1, value="Tip: Use Excel conditional formatting to color cells >=1.25x green, <1.25x red")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=9, color="888888")

    # Second matrix: by SDE variation
    row = 7 + len(rates) + 3
    ws.cell(row=row, column=1, value="DSCR BY SDE SCENARIO")
    ws.cell(row=row, column=1).font = Font(name="Calibri", bold=True, size=14)
    row += 1
    ws.cell(row=row, column=1, value="At current interest rate and deal terms, varying SDE and price")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=10, color="666666")

    sde_pcts = [-0.20, -0.10, 0, 0.10, 0.20]

    row += 1
    ws.cell(row=row, column=1, value="SDE ↓  /  Price →")
    ws.cell(row=row, column=1).font = HEADER_FONT
    ws.cell(row=row, column=1).fill = HEADER_FILL
    for j, pct in enumerate(price_pcts):
        c = j + 2
        if pct == 0:
            label = "Base Price"
        else:
            label = f"{pct:+.0%}"
        ws.cell(row=row, column=c, value=label)
        ws.cell(row=row, column=c).font = HEADER_FONT
        ws.cell(row=row, column=c).fill = HEADER_FILL
        ws.cell(row=row, column=c).alignment = Alignment(horizontal="center")

    header_row_2 = row

    # Price row
    row += 1
    ws.cell(row=row, column=1, value="Purchase Price")
    ws.cell(row=row, column=1).font = Font(name="Calibri", italic=True, size=9)
    for j, pct in enumerate(price_pcts):
        c = j + 2
        ws.cell(row=row, column=c).value = f"={price_ref}*(1+{pct})"
        ws.cell(row=row, column=c).number_format = '$#,##0'
        ws.cell(row=row, column=c).font = Font(name="Calibri", italic=True, size=9)
        ws.cell(row=row, column=c).alignment = Alignment(horizontal="center")

    sba_rate_ref = f"{de}!B{econ_refs['sba_rate_row']}"

    for i, sde_pct in enumerate(sde_pcts):
        r = row + 1 + i
        if sde_pct == 0:
            label = f"Base SDE"
        else:
            label = f"SDE {sde_pct:+.0%}"
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=1).font = Font(name="Calibri", bold=True)

        for j, price_pct in enumerate(price_pcts):
            c = j + 2
            price_formula = f"{price_ref}*(1+{price_pct})"
            sba_loan = f"ROUND({price_formula}*{sba_pct_ref},0)"
            seller_note = f"ROUND({price_formula}*0.1,0)"
            adj_eff_sde = f"({sde_ref}*(1+{sde_pct})-{replacement_ref})"

            sba_pmt = f"(-PMT({sba_rate_ref}/12,{sba_term_ref}*12,{sba_loan})*12)"
            seller_pmt = f"(-PMT({seller_rate_ref}/12,{seller_amort_ref}*12,{seller_note})*12)"

            formula = f"={adj_eff_sde}/({sba_pmt}+{seller_pmt})"
            ws.cell(row=r, column=c).value = formula
            ws.cell(row=r, column=c).number_format = DSCR_FMT
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center")

    ws.freeze_panes = "A1"


def main():
    parser = argparse.ArgumentParser(description="Generate P&L + DSCR workbook")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path (default: deal folder)")
    args = parser.parse_args()

    deal_dir = "deals/number-one-home-care-agency"
    if args.output:
        output_path = args.output
    else:
        output_path = f"{deal_dir}/Number One Home Care Agency - Financial Model.xlsx"

    wb = Workbook()

    pnl_refs = build_pnl_sheet(wb)
    econ_refs = build_deal_economics_sheet(wb, pnl_refs)
    build_sensitivity_sheet(wb, econ_refs)

    wb.save(output_path)
    print(f"Workbook saved to: {output_path}")


if __name__ == "__main__":
    main()
