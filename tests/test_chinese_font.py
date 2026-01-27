"""Test script to verify Chinese font rendering in matplotlib."""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import os

# Import visualization module to trigger font configuration
from utils import visualization

def test_chinese_font():
    """Test if matplotlib can render Chinese characters properly."""

    print("Testing Chinese font configuration...")

    # Get the detected CJK font
    cjk_font = visualization.get_cjk_font()
    print(f"Detected CJK font: {cjk_font}")

    # Apply CJK font configuration
    visualization.apply_cjk_font()

    print(f"Current font.sans-serif after apply: {plt.rcParams['font.sans-serif']}")

    # List available CJK fonts
    print("\nAvailable CJK-like fonts on system:")
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    cjk_fonts = [f for f in available_fonts if any(x in f for x in ['Fang', 'Hei', 'Gothic', 'Ming', 'Song', 'Yahei', 'SimHei', 'SimSun'])]
    for font in sorted(cjk_fonts):
        print(f"  - {font}")

    # Create a simple test plot with Chinese labels
    fig, ax = plt.subplots(figsize=(8, 6))

    # Sample data with Chinese labels
    categories = ['产品包类型', '产品ID', '原价(元)', '销售价(元)']
    values = [25, 80, 50, 30]

    ax.bar(categories, values)
    ax.set_xlabel('产品分类')
    ax.set_ylabel('数值')
    ax.set_title('中文字体测试 - Chinese Font Test')

    # Save the test plot
    output_dir = "temp/test"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "chinese_font_test.png")

    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"\n✅ Test plot saved to: {output_path}")
    print("Please open this image to verify Chinese characters are displaying correctly.")
    print("If you see boxes (□) instead of Chinese characters, font configuration needs adjustment.")

    return output_path

if __name__ == "__main__":
    test_chinese_font()
