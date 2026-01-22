"""HTML utilities for proper Unicode and CJK character rendering."""

import os
from pathlib import Path


def fix_html_cjk_encoding(filepath: str):
    """
    Fix HTML file encoding to properly display Chinese and other CJK characters.

    This function:
    1. Ensures UTF-8 encoding declaration is present
    2. Adds CSS with font families that support CJK characters
    3. Ensures proper meta charset tags

    Args:
        filepath: Path to the HTML file to fix
    """
    try:
        # Read the HTML file with UTF-8 encoding
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Ensure UTF-8 encoding declaration
        if '<meta charset="utf-8">' not in html_content.lower():
            # Add UTF-8 meta tag if missing
            if '<head>' in html_content:
                html_content = html_content.replace(
                    '<head>',
                    '<head>\n    <meta charset="UTF-8">'
                )

        # CSS for CJK (Chinese, Japanese, Korean) font support
        cjk_font_css = '''
    <style>
        /* CJK Font Support */
        html, body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei',
                         'PingFang SC', 'Hiragino Sans GB', 'Hiragino Kaku Gothic Pro',
                         'Noto Sans CJK SC', 'Noto Sans TC', 'Noto Sans JP',
                         SimSun, 'Arial Unicode MS', sans-serif;
        }

        /* Ensure all text elements use CJK-compatible fonts */
        body, h1, h2, h3, h4, h5, h6, p, div, span, a, li, td, th, label,
        input, textarea, button, .text, .content {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei',
                         'PingFang SC', 'Hiragino Sans GB', 'Hiragino Kaku Gothic Pro',
                         'Noto Sans CJK SC', 'Noto Sans TC', 'Noto Sans JP',
                         SimSun, 'Arial Unicode MS', sans-serif !important;
        }

        /* Monospace fonts for code */
        code, pre, .code {
            font-family: 'Courier New', 'Microsoft YaHei Mono', monospace !important;
        }
    </style>
    '''

        # Only add CSS if not already present
        if 'Microsoft YaHei' not in html_content:
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', cjk_font_css + '\n</head>')
            elif '<body>' in html_content:
                html_content = html_content.replace('<body>', cjk_font_css + '\n<body>')

        # Write back with UTF-8 encoding
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True

    except Exception as e:
        print(f"Warning: Could not fix CJK encoding in HTML file {filepath}: {e}")
        return False


def generate_html_report(title: str, content: str, output_path: str,
                        include_cjk_fonts: bool = True) -> bool:
    """
    Generate a simple HTML report with proper CJK support.

    Args:
        title: HTML page title
        content: HTML content to include
        output_path: Where to save the HTML file
        include_cjk_fonts: Whether to include CJK font CSS

    Returns:
        bool: True if successful
    """
    try:
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            margin: 20px;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei',
                         'PingFang SC', 'Hiragino Sans GB', sans-serif;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
    </style>
    {"" if not include_cjk_fonts else '''
    <style>
        /* CJK Font Support */
        body, h1, h2, h3, h4, h5, h6, p, div, span, a, li, td, th, label {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei',
                         'PingFang SC', 'Hiragino Sans GB', 'Hiragino Kaku Gothic Pro',
                         'Noto Sans CJK SC', 'Noto Sans TC', 'Noto Sans JP',
                         SimSun, 'Arial Unicode MS', sans-serif !important;
        }}
    </style>
    '''}
</head>
<body>
    <h1>{title}</h1>
    {content}
</body>
</html>
'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)

        return True

    except Exception as e:
        print(f"Error generating HTML report: {e}")
        return False
