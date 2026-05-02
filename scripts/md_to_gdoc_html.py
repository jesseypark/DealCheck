#!/usr/bin/env python3
"""Convert markdown files to styled HTML with inline styles for Google Docs import.

Google Docs strips <style> blocks and external CSS. Inline style="" attributes
on each element are preserved during HTML-to-Google-Doc conversion.
"""

import markdown
import sys
import base64
import re


def _inline_styles(html_body):
    """Replace tags with inline-styled equivalents that Google Docs preserves."""

    html_body = re.sub(
        r'<h1>(.*?)</h1>',
        r'<h1 style="font-size:18pt;color:#1a73e8;border-bottom:2px solid #1a73e8;padding-bottom:6px;font-family:Arial,sans-serif;">\1</h1>',
        html_body
    )
    html_body = re.sub(
        r'<h2>(.*?)</h2>',
        r'<h2 style="font-size:14pt;color:#202124;border-bottom:1px solid #dadce0;padding-bottom:4px;margin-top:24px;font-family:Arial,sans-serif;">\1</h2>',
        html_body
    )
    html_body = re.sub(
        r'<h3>(.*?)</h3>',
        r'<h3 style="font-size:12pt;color:#5f6368;margin-top:18px;font-family:Arial,sans-serif;">\1</h3>',
        html_body
    )

    html_body = re.sub(
        r'<table>',
        '<table style="border-collapse:collapse;width:100%;margin:12px 0;font-family:Arial,sans-serif;">',
        html_body
    )

    def style_header_row(match):
        row_content = match.group(1)
        row_content = re.sub(
            r'<th>(.*?)</th>',
            r'<th style="background-color:#1a73e8;color:white;padding:8px 12px;text-align:left;font-size:10pt;font-weight:bold;">\1</th>',
            row_content
        )
        return f'<tr>{row_content}</tr>'

    parts = html_body.split('</thead>')
    if len(parts) > 1:
        parts[0] = re.sub(r'<tr>(.*?)</tr>', style_header_row, parts[0], flags=re.DOTALL)
        html_body = '</thead>'.join(parts)

    row_count = [0]
    def style_body_row(match):
        row_content = match.group(1)
        row_count[0] += 1
        bg = '#f8f9fa' if row_count[0] % 2 == 0 else '#ffffff'
        row_content = re.sub(
            r'<td>(.*?)</td>',
            rf'<td style="padding:6px 12px;border-bottom:1px solid #dadce0;font-size:10pt;background-color:{bg};">\1</td>',
            row_content
        )
        return f'<tr style="background-color:{bg};">{row_content}</tr>'

    parts = html_body.split('<tbody>')
    if len(parts) > 1:
        row_count[0] = 0
        parts[1] = re.sub(r'<tr>(.*?)</tr>', style_body_row, parts[1], flags=re.DOTALL)
        html_body = '<tbody>'.join(parts)

    html_body = re.sub(
        r'<pre><code>(.*?)</code></pre>',
        r'<pre style="background-color:#f1f3f4;padding:12px 16px;border-radius:4px;font-size:10pt;line-height:1.4;font-family:Courier New,monospace;white-space:pre-wrap;"><code>\1</code></pre>',
        html_body,
        flags=re.DOTALL
    )
    html_body = re.sub(
        r'<code>(.*?)</code>',
        r'<code style="background-color:#f1f3f4;padding:2px 6px;font-family:Courier New,monospace;font-size:10pt;">\1</code>',
        html_body
    )

    html_body = re.sub(
        r'<blockquote>',
        '<blockquote style="border-left:4px solid #1a73e8;margin:12px 0;padding:8px 16px;background-color:#e8f0fe;">',
        html_body
    )

    html_body = re.sub(
        r'<p>(.*?)</p>',
        r'<p style="font-family:Arial,sans-serif;font-size:11pt;line-height:1.5;color:#1a1a1a;">\1</p>',
        html_body,
        flags=re.DOTALL
    )

    html_body = re.sub(
        r'<li>(.*?)</li>',
        r'<li style="font-family:Arial,sans-serif;font-size:11pt;margin-bottom:4px;color:#1a1a1a;">\1</li>',
        html_body,
        flags=re.DOTALL
    )

    html_body = re.sub(
        r'<hr\s*/?>',
        '<hr style="border:none;border-top:1px solid #dadce0;margin:20px 0;">',
        html_body
    )

    return html_body


def convert(md_path):
    with open(md_path, 'r') as f:
        md_content = f.read()

    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code']
    )

    styled_body = _inline_styles(html_body)

    html = f'<html><body>{styled_body}</body></html>'

    return base64.b64encode(html.encode('utf-8')).decode('utf-8')


if __name__ == '__main__':
    print(convert(sys.argv[1]))
