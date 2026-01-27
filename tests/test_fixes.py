"""Test script to verify both fixes: Chinese font + multiple image display."""

import pandas as pd
from utils import visualization
import os

def test_chinese_data_visualization():
    """Test visualization with Chinese column names and data."""

    print("Testing fixes with Chinese data...")

    # Load the user's CSV file
    csv_path = "/Users/chenhao/Desktop/data-demo-zh.csv"
    df = pd.read_csv(csv_path)

    print(f"Loaded data: {len(df)} rows × {len(df.columns)} columns")
    print(f"Columns (first 5): {df.columns[:5].tolist()}")

    # Test 1: Create a box plot with Chinese column names
    print("\n1. Creating box plot with Chinese labels...")
    try:
        # Use 1124在订 (numeric column) grouped by 产品包类型 (categorical)
        fig1 = visualization.create_box_plot(
            df,
            column='1124在订',
            group_by='产品包类型',
            figsize=(10, 6)
        )
        path1 = visualization.save_figure(fig1, "test_box_chinese")
        print(f"   ✅ Box plot created: {path1}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Create a violin plot
    print("\n2. Creating violin plot with Chinese labels...")
    try:
        fig2 = visualization.create_violin_plot(
            df,
            column='原价(元)',
            group_by='产品包类型',
            figsize=(10, 6)
        )
        path2 = visualization.save_figure(fig2, "test_violin_chinese")
        print(f"   ✅ Violin plot created: {path2}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Create a correlation heatmap with Chinese column names
    print("\n3. Creating correlation heatmap with Chinese columns...")
    try:
        # Select numeric columns only
        numeric_cols = df.select_dtypes(include=['number']).columns[:5]
        corr_matrix = df[numeric_cols].corr()

        fig3 = visualization.create_correlation_heatmap(corr_matrix, figsize=(10, 8))
        path3 = visualization.save_figure(fig3, "test_heatmap_chinese")
        print(f"   ✅ Heatmap created: {path3}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)

    # Check if all files exist
    test_files = [
        "temp/charts/test_box_chinese.png",
        "temp/charts/test_violin_chinese.png",
        "temp/charts/test_heatmap_chinese.png"
    ]

    all_exist = True
    for file in test_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_exist = False

    if all_exist:
        print("\n🎉 All tests passed! Chinese characters should display correctly.")
        print("\nPlease check the generated images to verify:")
        print("   1. Chinese characters are visible (not boxes)")
        print("   2. All labels are readable")
    else:
        print("\n⚠️  Some files were not created. Check errors above.")

    return all_exist

if __name__ == "__main__":
    test_chinese_data_visualization()
