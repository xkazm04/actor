"""
Report Formatters - Format conversion utilities.
Converts between Markdown, HTML, JSON formats.
"""

import json
from typing import Dict


def format_markdown_to_html(markdown: str) -> str:
    """
    Convert markdown to HTML.
    Basic implementation - for production use markdown library.
    
    Args:
        markdown: Markdown text
        
    Returns:
        HTML string
    """
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        h3 { color: #777; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
        blockquote { border-left: 4px solid #ccc; margin-left: 0; padding-left: 20px; color: #666; }
    </style>
</head>
<body>
""")
    
    # Simple markdown parsing
    lines = markdown.split('\n')
    in_code = False
    
    for line in lines:
        if line.startswith('# '):
            html_parts.append(f'<h1>{line[2:]}</h1>\n')
        elif line.startswith('## '):
            html_parts.append(f'<h2>{line[3:]}</h2>\n')
        elif line.startswith('### '):
            html_parts.append(f'<h3>{line[4:]}</h3>\n')
        elif line.startswith('- ') or line.startswith('* '):
            html_parts.append(f'<li>{line[2:]}</li>\n')
        elif line.strip() == '':
            html_parts.append('<p></p>\n')
        else:
            # Convert links
            import re
            line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', line)
            html_parts.append(f'<p>{line}</p>\n')
    
    html_parts.append("</body>\n</html>")
    return ''.join(html_parts)


def format_json_report(data: Dict) -> str:
    """
    Format JSON report data as readable text.
    
    Args:
        data: Report data dictionary
        
    Returns:
        Formatted text string
    """
    lines = []
    
    if 'query' in data:
        lines.append(f"# Research Report: {data['query']}\n\n")
    
    if 'executive_summary' in data:
        lines.append("## Executive Summary\n\n")
        lines.append(f"{data['executive_summary']}\n\n")
    
    if 'main_findings' in data:
        lines.append("## Main Findings\n\n")
        findings = data['main_findings']
        if isinstance(findings, dict):
            for key, value in findings.items():
                lines.append(f"### {key}\n\n{value}\n\n")
        else:
            lines.append(f"{findings}\n\n")
    
    if 'conclusions' in data:
        lines.append("## Conclusions\n\n")
        lines.append(f"{data['conclusions']}\n\n")
    
    return ''.join(lines)


def export_to_json(data: Dict, pretty: bool = True) -> str:
    """
    Export report data to JSON string.
    
    Args:
        data: Report data dictionary
        pretty: Whether to format JSON nicely
        
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, ensure_ascii=False)



