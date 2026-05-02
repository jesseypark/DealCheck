#!/usr/bin/env python3
"""Convert markdown files to styled standalone HTML with dashboard-style cards and severity colors."""

import sys
import re


CSS = """
:root {
  --bg: #ffffff;
  --surface: #f8f9fa;
  --surface2: #f1f3f5;
  --border: #dee2e6;
  --text: #212529;
  --text-dim: #6c757d;
  --accent: #1a73e8;
  --critical: #cc0033;
  --critical-bg: rgba(204,0,51,.06);
  --warning: #e69100;
  --warning-bg: rgba(230,145,0,.06);
  --watch: #2e7d32;
  --watch-bg: rgba(46,125,50,.06);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 2rem;
  max-width: 920px;
  margin: 0 auto;
}

/* ─── Header ─── */
.header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}
.header h1 {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
  margin-bottom: .25rem;
}
.header-sub {
  color: var(--text-dim);
  font-size: .88rem;
}

/* ─── Sections (cards) ─── */
.section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.25rem;
}
.section-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--text-dim);
  margin-bottom: 1rem;
}

/* ─── Severity headers ─── */
.flag-group { margin-bottom: 1.5rem; }
.flag-group:last-child { margin-bottom: 0; }
.flag-group-header {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin-bottom: .75rem;
  font-weight: 700;
  font-size: .85rem;
}
.flag-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.flag-dot-critical { background: var(--critical); box-shadow: 0 0 6px rgba(204,0,51,.3); }
.flag-dot-warning  { background: var(--warning);  box-shadow: 0 0 6px rgba(230,145,0,.3); }
.flag-dot-watch    { background: var(--watch);    box-shadow: 0 0 6px rgba(46,125,50,.2); }

/* ─── Flag cards ─── */
.flag-card {
  padding: 1rem 1.15rem;
  border-radius: 8px;
  margin-bottom: .6rem;
  font-size: .85rem;
}
.flag-card-critical { background: var(--critical-bg); border-left: 3px solid var(--critical); }
.flag-card-warning  { background: var(--warning-bg);  border-left: 3px solid var(--warning); }
.flag-card-watch    { background: var(--watch-bg);    border-left: 3px solid var(--watch); }
.flag-title {
  font-weight: 700;
  margin-bottom: .35rem;
}
.flag-detail {
  color: var(--text-dim);
  font-size: .82rem;
  margin-bottom: .25rem;
}
.flag-action {
  font-size: .78rem;
  color: var(--accent);
  font-style: italic;
  margin-top: .35rem;
}

/* ─── Tables ─── */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: .82rem;
  font-variant-numeric: tabular-nums;
  margin: .5rem 0;
}
th {
  text-align: left;
  font-weight: 600;
  padding: .5rem .6rem;
  border-bottom: 2px solid var(--border);
  color: var(--text-dim);
  font-size: .75rem;
  text-transform: uppercase;
  letter-spacing: .04em;
}
td {
  padding: .5rem .6rem;
  border-bottom: 1px solid rgba(0,0,0,.06);
}
tr:last-child td { border-bottom: none; }
.num { text-align: right; }

/* ─── Status colors ─── */
.pass { color: var(--watch); font-weight: 600; }
.fail { color: var(--critical); font-weight: 600; }
.marginal { color: var(--warning); font-weight: 600; }
.highlight { color: var(--accent); font-weight: 600; }

/* ─── Code blocks ─── */
pre {
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 1rem 1.25rem;
  border-radius: 8px;
  font-family: 'SF Mono', 'Menlo', 'Courier New', monospace;
  font-size: .8rem;
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--text);
  overflow-x: auto;
  margin: .75rem 0;
}
pre code {
  background: none;
  padding: 0;
  font-size: inherit;
}
code {
  background: var(--surface2);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'SF Mono', 'Menlo', 'Courier New', monospace;
  font-size: .8rem;
}

/* ─── Blockquotes ─── */
blockquote {
  border-left: 3px solid var(--accent);
  margin: .75rem 0;
  padding: .6rem 1rem;
  background: rgba(26,115,232,.04);
  border-radius: 0 6px 6px 0;
  font-size: .85rem;
}
blockquote p {
  margin: .25rem 0;
  color: var(--text-dim);
}

/* ─── Callouts ─── */
.callout {
  margin: .75rem 0;
  padding: .75rem 1rem;
  border-radius: 0 6px 6px 0;
  font-size: .82rem;
}
.callout-info { background: rgba(26,115,232,.05); border-left: 3px solid var(--accent); }
.callout-warning { background: var(--warning-bg); border-left: 3px solid var(--warning); }

/* ─── Misc ─── */
hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.5rem 0;
}
h2.section-heading {
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--text-dim);
  margin: 0 0 1rem 0;
  border: none;
  padding: 0;
}
p {
  font-size: .88rem;
  margin: .4rem 0;
}
p.detail {
  color: var(--text-dim);
  font-style: italic;
  margin-left: 16px;
  font-size: .82rem;
}
li {
  font-size: .88rem;
  margin: .3rem 0 .3rem 1.5rem;
}
strong { font-weight: 700; }
em { font-style: italic; color: var(--text-dim); }
"""


def _severity_class(text):
    t = text.lower()
    if 'critical' in t or 'fail' in t:
        return 'critical'
    if 'warning' in t:
        return 'warning'
    if 'watch' in t or 'pass' in t:
        return 'watch'
    return None


def _color_keywords(text):
    def repl(m):
        kw = m.group(0)
        upper = kw.upper()
        if 'FAIL' in upper or upper == 'DOES NOT PENCIL':
            return f'<span class="fail">{kw}</span>'
        if upper in ('PASS', 'PASSES', 'FEASIBLE'):
            return f'<span class="pass">{kw}</span>'
        if 'MARGINAL' in upper:
            return f'<span class="marginal">{kw}</span>'
        return kw
    return re.sub(
        r'\b(PASS|PASSES|FAIL|FAILS|FAILS BADLY|DOES NOT PENCIL|MARGINAL|FEASIBLE)\b',
        repl, text)


def _inline_format(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def _status_emoji(text):
    text = text.replace('✅', '<span class="pass">&#x2705;</span>')
    text = text.replace('❌', '<span class="fail">&#x274C;</span>')
    return text


def convert(md_path, out_path=None):
    with open(md_path, 'r') as f:
        lines = f.read().split('\n')

    html_parts = []
    i = 0
    in_code = False
    code_lines = []
    in_table = False
    table_rows = []
    in_blockquote = False
    bq_lines = []
    current_severity = None
    in_section = False
    in_flag_group = False
    pending_flag_paragraphs = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        html_parts.append('<table>')
        for ri, row in enumerate(table_rows):
            if ri == 0:
                html_parts.append('<thead><tr>')
                for cell in row:
                    cell_html = _inline_format(_color_keywords(_status_emoji(cell)))
                    html_parts.append(f'<th>{cell_html}</th>')
                html_parts.append('</tr></thead><tbody>')
            else:
                html_parts.append('<tr>')
                for cell in row:
                    cell_html = _inline_format(_color_keywords(_status_emoji(cell)))
                    html_parts.append(f'<td>{cell_html}</td>')
                html_parts.append('</tr>')
        html_parts.append('</tbody></table>')
        in_table = False
        table_rows = []

    def flush_blockquote():
        nonlocal in_blockquote, bq_lines
        if not bq_lines:
            in_blockquote = False
            return
        html_parts.append('<blockquote>')
        for bl in bq_lines:
            html_parts.append(f'<p>{_inline_format(_color_keywords(bl))}</p>')
        html_parts.append('</blockquote>')
        in_blockquote = False
        bq_lines = []

    def close_flag_card():
        nonlocal pending_flag_paragraphs
        if pending_flag_paragraphs:
            for pf in pending_flag_paragraphs:
                html_parts.append(pf)
            html_parts.append('</div>')
            pending_flag_paragraphs = []

    def close_flag_group():
        nonlocal in_flag_group
        if in_flag_group:
            close_flag_card()
            html_parts.append('</div>')
            in_flag_group = False

    def close_section():
        nonlocal in_section
        if in_section:
            close_flag_group()
            html_parts.append('</div>')
            in_section = False

    def open_section(title):
        nonlocal in_section
        close_section()
        in_section = True
        html_parts.append('<div class="section">')
        html_parts.append(f'<div class="section-title">{_inline_format(title)}</div>')

    first_h1_done = False
    header_emitted = False

    # Pre-scan: collect header lines (before first ## or # ) for non-standard formats
    header_lines = []
    for pre_i, pre_line in enumerate(lines):
        s = pre_line.strip()
        if not s or re.match(r'^={3,}$', s) or s.startswith('═'):
            continue
        if pre_line.startswith('# ') or pre_line.startswith('## '):
            break
        # Check if this looks like a header line (DEAL SCORECARD:, Industry:, Location:, etc.)
        if any(pre_line.strip().startswith(k) for k in ['DEAL SCORECARD:', 'Industry:', 'Location:', 'Last Updated:', 'Sources:']):
            header_lines.append(pre_line.strip())
        else:
            break

    if header_lines:
        html_parts.append('<div class="header">')
        title = header_lines[0].replace('DEAL SCORECARD:', '').strip()
        html_parts.append(f'<h1>{title}</h1>')
        if len(header_lines) > 1:
            html_parts.append(f'<div class="header-sub">{" &middot; ".join(header_lines[1:])}</div>')
        html_parts.append('</div>')
        header_emitted = True
        first_h1_done = True

    while i < len(lines):
        line = lines[i]

        # Code block toggle
        if line.startswith('```'):
            if not in_code:
                if in_table:
                    flush_table()
                if in_blockquote:
                    flush_blockquote()
                in_code = True
                code_lines = []
                i += 1
                continue
            else:
                in_code = False
                code_text = '\n'.join(code_lines)
                code_text = _color_keywords(code_text)
                html_parts.append(f'<pre><code>{code_text}</code></pre>')
                i += 1
                continue

        if in_code:
            code_lines.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue

        # Bold-starting severity items (check before table to avoid | in "RF-011 | Title")
        if line.strip().startswith('**') and current_severity and '|' in line:
            if in_table:
                flush_table()
            if in_blockquote:
                flush_blockquote()
            close_flag_card()
            title_text = re.sub(r'^\*\*(.+?)\*\*$', r'\1', line.strip())
            if title_text == line.strip():
                title_text = line.strip().replace('**', '')
            html_parts.append(f'<div class="flag-card flag-card-{current_severity}">')
            html_parts.append(f'<div class="flag-title">{title_text}</div>')
            pending_flag_paragraphs = []
            i += 1
            continue

        # Table rows
        if '|' in line and not line.strip().startswith('```'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                i += 1
                continue
            if in_blockquote:
                flush_blockquote()
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            i += 1
            continue

        if in_table:
            flush_table()

        # Blockquotes
        if line.startswith('> '):
            if not in_blockquote:
                in_blockquote = True
                bq_lines = []
            bq_lines.append(line[2:])
            i += 1
            continue
        elif in_blockquote:
            flush_blockquote()

        # Decorators and blank lines
        if line.startswith('═') or re.match(r'^={3,}$', line.strip()) or line.strip() == '':
            i += 1
            continue

        # Track severity
        stripped = line.strip().lower()
        if '### critical' in stripped:
            current_severity = 'critical'
        elif '### warning' in stripped:
            current_severity = 'warning'
        elif '### watch' in stripped:
            current_severity = 'watch'
        elif line.startswith('## ') and 'red flag' not in stripped:
            current_severity = None

        # H1 — becomes header div
        if line.startswith('# ') and not line.startswith('## '):
            if not first_h1_done:
                title_text = line[2:].strip()
                # Try to extract subtitle from colon
                html_parts.append('<div class="header">')
                html_parts.append(f'<h1>{_inline_format(title_text)}</h1>')
                # Look ahead for subtitle-like lines
                first_h1_done = True
            else:
                html_parts.append(f'<h1>{_inline_format(line[2:].strip())}</h1>')

        # H2 — header or section card
        elif line.startswith('## '):
            title = line[3:].strip()
            # "## DEAL SCORECARD: ..." becomes a header if none emitted yet
            if title.upper().startswith('DEAL SCORECARD') and not header_emitted:
                header_emitted = True
                first_h1_done = True
                deal_name = re.sub(r'^DEAL SCORECARD:\s*', '', title, flags=re.IGNORECASE).strip()
                html_parts.append('<div class="header">')
                html_parts.append(f'<h1>{deal_name}</h1>')
                # Look ahead for subtitle lines
                sub_parts = []
                j = i + 1
                while j < len(lines):
                    sl = lines[j].strip()
                    if not sl:
                        j += 1
                        continue
                    if sl.startswith('#') or sl.startswith('---') or sl.startswith('```') or sl.startswith('|'):
                        break
                    sub_parts.append(sl)
                    j += 1
                if sub_parts:
                    html_parts.append(f'<div class="header-sub">{" &middot; ".join(sub_parts)}</div>')
                html_parts.append('</div>')
                i = j
                continue
            close_flag_group()
            open_section(title)

        # H3 — severity flag groups or subsection
        elif line.startswith('### '):
            title = line[4:].strip()
            sev = _severity_class(title)
            if sev and current_severity:
                close_flag_group()
                in_flag_group = True
                dot_class = f'flag-dot-{sev}'
                html_parts.append('<div class="flag-group">')
                html_parts.append(f'<div class="flag-group-header"><div class="flag-dot {dot_class}"></div>{_inline_format(title)}</div>')
            else:
                close_flag_group()
                html_parts.append(f'<div style="font-weight:600;font-size:.85rem;margin:1rem 0 .5rem 0">{_inline_format(title)}</div>')

        # HR — close current section if inside one
        elif line.startswith('---'):
            if first_h1_done and not in_section:
                html_parts.append('</div>')
            elif in_section:
                pass

        # Bold-starting severity items (no pipe)
        elif line.strip().startswith('**') and current_severity:
            close_flag_card()
            raw = line.strip()
            title_text = re.sub(r'^\*\*(.+?)\*\*$', r'\1', raw)
            if title_text == raw:
                title_text = raw.replace('**', '')
            html_parts.append(f'<div class="flag-card flag-card-{current_severity}">')
            html_parts.append(f'<div class="flag-title">{_color_keywords(title_text)}</div>')
            pending_flag_paragraphs = []

        # Arrow detail lines
        elif line.strip().startswith('→') or line.strip().startswith('->'):
            text = _inline_format(_color_keywords(line.strip()))
            if pending_flag_paragraphs is not None and in_flag_group:
                pending_flag_paragraphs.append(f'<div class="flag-action">{text}</div>')
            else:
                html_parts.append(f'<p class="detail">{text}</p>')

        # Bullet lists
        elif line.startswith('- ') or line.startswith('* '):
            content = _inline_format(_color_keywords(line[2:]))
            if pending_flag_paragraphs is not None and in_flag_group:
                pending_flag_paragraphs.append(f'<li style="font-size:.82rem;color:var(--text-dim);margin-left:1rem">{content}</li>')
            else:
                html_parts.append(f'<li>{content}</li>')

        # Numbered lists
        elif re.match(r'^\d+\.\s', line):
            content = _inline_format(_color_keywords(re.sub(r'^\d+\.\s', '', line)))
            html_parts.append(f'<li>{content}</li>')

        # Regular text
        elif line.strip():
            # Skip lines already emitted as header
            if header_emitted and any(line.strip().startswith(k) for k in ['DEAL SCORECARD:', 'Industry:', 'Location:', 'Last Updated:', 'Sources:']):
                i += 1
                continue
            text = _inline_format(_color_keywords(_status_emoji(line.strip())))
            if pending_flag_paragraphs is not None and in_flag_group:
                pending_flag_paragraphs.append(f'<div class="flag-detail">{text}</div>')
            else:
                html_parts.append(f'<p>{text}</p>')

        i += 1

    if in_table:
        flush_table()
    if in_blockquote:
        flush_blockquote()
    close_section()

    body = '\n'.join(html_parts)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
{CSS}
</style>
</head>
<body>
{body}
</body>
</html>"""

    if out_path is None:
        out_path = md_path.rsplit('.', 1)[0] + '.html'
    with open(out_path, 'w') as f:
        f.write(html)
    return out_path


if __name__ == '__main__':
    out = None
    if len(sys.argv) > 2:
        out = sys.argv[2]
    path = convert(sys.argv[1], out)
    print(f"Saved: {path}")
