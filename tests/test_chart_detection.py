"""Test chart detection logic."""

import os
import glob
import time

# Simulate the detection logic
charts_dir = "temp/charts"

print("Testing chart detection logic...")
print("="*60)

# Step 1: Get existing charts
if os.path.exists(charts_dir):
    existing_charts = set(glob.glob(os.path.join(charts_dir, "*.png")))
    print(f"Step 1: Found {len(existing_charts)} existing charts")
    if existing_charts:
        for chart in list(existing_charts)[:3]:
            print(f"  - {os.path.basename(chart)}")
        if len(existing_charts) > 3:
            print(f"  ... and {len(existing_charts) - 3} more")
else:
    existing_charts = set()
    print(f"Step 1: Charts directory doesn't exist yet")

# Step 2: Simulate agent creating charts (wait a moment)
print(f"\nStep 2: Simulating agent run (creating charts)...")
print("  (In real app, agent would create charts here)")

# Step 3: Check for new charts
print(f"\nStep 3: Checking for new charts...")
if os.path.exists(charts_dir):
    current_charts = set(glob.glob(os.path.join(charts_dir, "*.png")))
    new_charts = current_charts - existing_charts

    print(f"  Total charts now: {len(current_charts)}")
    print(f"  New charts created: {len(new_charts)}")

    if new_charts:
        print("\n  New chart files:")
        for chart in sorted(new_charts):
            mtime = os.path.getmtime(chart)
            print(f"    - {os.path.basename(chart)} (modified: {time.ctime(mtime)})")
    else:
        print("  ❌ No new charts detected")

        # Debug: Check modification times of all charts
        print("\n  All charts with modification times:")
        all_charts = sorted(current_charts, key=os.path.getmtime, reverse=True)
        for i, chart in enumerate(all_charts[:5]):
            mtime = os.path.getmtime(chart)
            age_seconds = time.time() - mtime
            print(f"    {i+1}. {os.path.basename(chart)} - {age_seconds:.1f}s ago")
        if len(all_charts) > 5:
            print(f"    ... and {len(all_charts) - 5} more")
else:
    print("  ❌ Charts directory still doesn't exist")

print("\n" + "="*60)
print("Detection logic test complete")
