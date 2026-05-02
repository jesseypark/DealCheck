#!/usr/bin/env python3
"""Convert markdown files to styled PDF with color-coded severity indicators."""

import sys
import base64
import re
from fpdf import FPDF

# Severity colors
CRITICAL_RGB = (204, 0, 51)       # red
CRITICAL_BG = (255, 235, 238)     # light red
WARNING_RGB = (230, 145, 0)       # amber
WARNING_BG = (255, 243, 224)      # light amber
WATCH_RGB = (46, 125, 50)         # green
WATCH_BG = (232, 245, 233)        # light green
PASS_RGB = (46, 125, 50)
FAIL_RGB = (204, 0, 51)
MARGINAL_RGB = (230, 145, 0)
HEADER_BLUE = (26, 115, 232)
TABLE_HEADER_BG = (26, 115, 232)
TABLE_ALT_BG = (245, 247, 250)
CODE_BG = (241, 243, 244)
CODE_TEXT = (55, 71, 79)
TEXT_DEFAULT = (32, 33, 36)
TEXT_DIM = (95, 99, 104)
DIVIDER = (218, 220, 224)


def _severity_from_line(line):
    lower = line.lower()
    if 'critical' in lower or 'fail' in lower:
        return 'critical'
    if 'warning' in lower:
        return 'warning'
    if 'watch' in lower or 'pass' in lower:
        return 'watch'
    return None


def _color_for_cell(text):
    t = text.strip().upper()
    if t in ('FAIL', 'FAILS', 'FAILS BADLY', 'DOES NOT PENCIL'):
        return FAIL_RGB
    if t in ('PASS', 'PASSES', 'FEASIBLE'):
        return PASS_RGB
    if t in ('MARGINAL', 'MARGINAL — fails post-standby'):
        return MARGINAL_RGB
    if 'FAIL' in t:
        return FAIL_RGB
    if 'PASS' in t:
        return PASS_RGB
    if 'MARGINAL' in t:
        return MARGINAL_RGB
    return None


class ScorecardPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')


def convert(md_path, out_path=None):
    with open(md_path, 'r') as f:
        md_content = f.read()

    pdf = ScorecardPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    font_dir = '/System/Library/Fonts/Supplemental'
    pdf.add_font('Arial', '', f'{font_dir}/Arial Bold.ttf')
    pdf.add_font('Arial', 'B', f'{font_dir}/Arial Bold.ttf')
    pdf.add_font('Arial', 'I', f'{font_dir}/Arial Italic.ttf')
    pdf.add_font('CourierNew', '', f'{font_dir}/Courier New.ttf')

    pdf.add_page()

    lines = md_content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []
    current_severity = None

    while i < len(lines):
        line = lines[i]

        # Code block start
        if line.startswith('```') and not in_code_block:
            if in_table:
                _flush_table(pdf, table_rows)
                in_table = False
                table_rows = []
            in_code_block = True
            code_lines = []
            i += 1
            continue

        # Code block end
        if line.startswith('```') and in_code_block:
            in_code_block = False
            _flush_code(pdf, code_lines)
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table rows
        if '|' in line and not line.strip().startswith('```'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                i += 1
                continue
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            i += 1
            continue

        if in_table:
            _flush_table(pdf, table_rows)
            in_table = False
            table_rows = []

        # Blank lines and decorators
        if line.startswith('═') or line.strip() == '':
            if line.strip() == '':
                pdf.ln(3)
            i += 1
            continue

        # Detect severity sections
        stripped = line.strip().lower()
        if '### critical' in stripped:
            current_severity = 'critical'
        elif '### warning' in stripped:
            current_severity = 'warning'
        elif '### watch' in stripped:
            current_severity = 'watch'
        elif line.startswith('## ') and 'red flag' not in stripped:
            current_severity = None

        # H1
        if line.startswith('# '):
            pdf.ln(4)
            pdf.set_font('Arial', 'B', 18)
            pdf.set_text_color(*HEADER_BLUE)
            pdf.cell(0, 10, line[2:].strip())
            pdf.ln(10)
            pdf.set_draw_color(*HEADER_BLUE)
            pdf.set_line_width(0.5)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + pdf.epw, pdf.get_y())
            pdf.ln(4)

        # H2
        elif line.startswith('## '):
            pdf.ln(6)
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(*TEXT_DEFAULT)
            pdf.cell(0, 8, line[3:].strip())
            pdf.ln(8)
            pdf.set_draw_color(*DIVIDER)
            pdf.set_line_width(0.3)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + pdf.epw, pdf.get_y())
            pdf.ln(3)

        # H3 — color-coded for severity sections
        elif line.startswith('### '):
            pdf.ln(4)
            title = line[4:].strip()
            sev = _severity_from_line(title)
            if sev == 'critical':
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(*CRITICAL_RGB)
                pdf.set_fill_color(*CRITICAL_BG)
                pdf.cell(0, 7, '  ' + title, fill=True)
            elif sev == 'warning':
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(*WARNING_RGB)
                pdf.set_fill_color(*WARNING_BG)
                pdf.cell(0, 7, '  ' + title, fill=True)
            elif sev == 'watch':
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(*WATCH_RGB)
                pdf.set_fill_color(*WATCH_BG)
                pdf.cell(0, 7, '  ' + title, fill=True)
            else:
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(*TEXT_DIM)
                pdf.cell(0, 7, title)
            pdf.ln(8)

        # HR
        elif line.startswith('---'):
            pdf.ln(4)
            pdf.set_draw_color(*DIVIDER)
            pdf.set_line_width(0.3)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + pdf.epw, pdf.get_y())
            pdf.ln(4)

        # Bullet lists
        elif line.startswith('- ') or line.startswith('* '):
            _write_rich_line(pdf, '  •  ' + line[2:], indent=5, severity=current_severity)

        # Numbered lists
        elif re.match(r'^\d+\.\s', line):
            num = re.match(r'^(\d+)\.\s', line).group(1)
            _write_rich_line(pdf, f'  {num}.  ' + re.sub(r'^\d+\.\s', '', line), indent=5, severity=current_severity)

        # Blockquotes
        elif line.startswith('> '):
            pdf.set_fill_color(232, 240, 254)
            pdf.set_x(pdf.get_x() + 5)
            _write_rich_line(pdf, line[2:], indent=5, fill=True)

        # Bold-starting lines with severity (red flag items like "**1. Title**")
        elif line.strip().startswith('**') and current_severity:
            _write_severity_line(pdf, line, current_severity)

        # Arrow lines (→) in italic
        elif line.strip().startswith('→') or line.strip().startswith('->'):
            _write_rich_line(pdf, line, indent=10, is_detail=True)

        # Regular text
        elif line.strip():
            _write_rich_line(pdf, line)

        i += 1

    if in_table:
        _flush_table(pdf, table_rows)

    if out_path is None:
        out_path = md_path.rsplit('.', 1)[0] + '.pdf'
    pdf.output(out_path)
    return out_path


def _flush_code(pdf, code_lines):
    pdf.ln(2)
    lh = 4.5
    for cl in code_lines:
        y = pdf.get_y()
        x = pdf.l_margin
        pdf.set_fill_color(*CODE_BG)
        pdf.rect(x, y, pdf.epw, lh, 'F')
        pdf.set_xy(x, y)
        pdf.set_font('CourierNew', '', 8)

        keyword_match = re.search(
            r'\b(PASS|PASSES|FAIL|FAILS|FAILS BADLY|DOES NOT PENCIL|MARGINAL|FEASIBLE)\b', cl)
        if keyword_match:
            before = '  ' + cl[:keyword_match.start()]
            keyword = keyword_match.group()
            after = cl[keyword_match.end():]

            pdf.set_text_color(*CODE_TEXT)
            pdf.write(lh, before)

            kw_upper = keyword.upper()
            if 'FAIL' in kw_upper or kw_upper == 'DOES NOT PENCIL':
                pdf.set_text_color(*FAIL_RGB)
            elif kw_upper in ('PASS', 'PASSES', 'FEASIBLE'):
                pdf.set_text_color(*PASS_RGB)
            elif 'MARGINAL' in kw_upper:
                pdf.set_text_color(*MARGINAL_RGB)
            pdf.write(lh, keyword)

            if after:
                pdf.set_text_color(*CODE_TEXT)
                pdf.write(lh, after)
        else:
            pdf.set_text_color(*CODE_TEXT)
            pdf.write(lh, '  ' + cl)

        pdf.ln(lh)
    pdf.ln(2)
    pdf.set_text_color(*TEXT_DEFAULT)


def _flush_table(pdf, rows):
    if not rows:
        return
    pdf.ln(2)
    num_cols = max(len(r) for r in rows)
    rh = 6

    # Calculate proportional column widths based on content
    pdf.set_font('Arial', 'B', 8)
    col_max = [0.0] * num_cols
    for row_data in rows:
        for ci in range(num_cols):
            raw = row_data[ci] if ci < len(row_data) else ''
            clean = raw.replace('**', '')
            w = pdf.get_string_width('  ' + clean) + 6
            col_max[ci] = max(col_max[ci], w)

    total = sum(col_max)
    if total <= pdf.epw:
        extra = pdf.epw - total
        col_w = [w + extra / num_cols for w in col_max]
    else:
        col_w = [w * pdf.epw / total for w in col_max]

    for ri, row_data in enumerate(rows):
        cells = []
        for ci in range(num_cols):
            raw = row_data[ci] if ci < len(row_data) else ''
            is_bold = raw.startswith('**') and raw.endswith('**')
            text = raw[2:-2] if is_bold else raw
            cells.append((text, is_bold))

        # Calculate row height accounting for text wrapping
        max_h = rh
        pdf.set_font('Arial', 'B', 8)
        for ci, (text, _) in enumerate(cells):
            tw = pdf.get_string_width('  ' + text)
            usable = col_w[ci] - 4
            if usable > 0 and tw > usable:
                n_lines = int(tw / usable) + 1
                max_h = max(max_h, n_lines * rh)

        if pdf.get_y() + max_h > pdf.h - pdf.b_margin:
            pdf.add_page()

        x0 = pdf.l_margin
        y0 = pdf.get_y()

        for ci, (text, is_bold) in enumerate(cells):
            if ri == 0:
                pdf.set_fill_color(*TABLE_HEADER_BG)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Arial', 'B', 8)
            else:
                cell_color = _color_for_cell(text)
                if cell_color:
                    pdf.set_text_color(*cell_color)
                    pdf.set_font('Arial', 'B', 8)
                elif is_bold:
                    pdf.set_text_color(*TEXT_DEFAULT)
                    pdf.set_font('Arial', 'B', 8)
                else:
                    pdf.set_text_color(*TEXT_DEFAULT)
                    pdf.set_font('Arial', '', 8)
                if ri % 2 == 0:
                    pdf.set_fill_color(*TABLE_ALT_BG)
                else:
                    pdf.set_fill_color(255, 255, 255)

            cx = x0 + sum(col_w[:ci])
            pdf.rect(cx, y0, col_w[ci], max_h, 'F')
            pdf.set_xy(cx, y0)
            pdf.multi_cell(col_w[ci], rh, '  ' + text, border=0)

        pdf.set_y(y0 + max_h)

    pdf.set_text_color(*TEXT_DEFAULT)
    pdf.ln(2)


def _write_severity_line(pdf, text, severity):
    """Write a bold-starting line with a colored left marker for severity."""
    colors = {
        'critical': (CRITICAL_RGB, CRITICAL_BG),
        'warning': (WARNING_RGB, WARNING_BG),
        'watch': (WATCH_RGB, WATCH_BG),
    }
    fg, bg = colors.get(severity, (TEXT_DEFAULT, (255, 255, 255)))

    x = pdf.get_x()
    y = pdf.get_y()

    # Colored left bar
    pdf.set_fill_color(*fg)
    pdf.rect(x, y, 2.5, 6, 'F')

    pdf.set_x(x + 6)
    _write_rich_line(pdf, text, indent=0)


def _write_rich_line(pdf, text, indent=0, fill=False, severity=None, is_detail=False):
    if is_detail:
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(*TEXT_DIM)
    else:
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*TEXT_DEFAULT)

    if indent:
        pdf.set_x(pdf.get_x() + indent)

    parts = re.split(r'(\*\*.*?\*\*|\*[^*]+\*|`[^`]+`)', text)
    line_height = 5.5

    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font('Arial', 'B', 10)
            if severity == 'critical':
                pdf.set_text_color(*CRITICAL_RGB)
            elif severity == 'warning':
                pdf.set_text_color(*WARNING_RGB)
            elif severity == 'watch':
                pdf.set_text_color(*WATCH_RGB)
            else:
                pdf.set_text_color(*TEXT_DEFAULT)
            pdf.write(line_height, part[2:-2])
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(*TEXT_DEFAULT)
        elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(*TEXT_DIM)
            pdf.write(line_height, part[1:-1])
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(*TEXT_DEFAULT)
        elif part.startswith('`') and part.endswith('`'):
            pdf.set_font('CourierNew', '', 8)
            pdf.set_text_color(*CODE_TEXT)
            pdf.write(line_height, part[1:-1])
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(*TEXT_DEFAULT)
        elif part:
            pdf.write(line_height, part)

    pdf.ln(line_height)


if __name__ == '__main__':
    out = None
    if len(sys.argv) > 2:
        out = sys.argv[2]
    path = convert(sys.argv[1], out)
    print(f"Saved: {path}")
