#!/usr/bin/env python3
"""
Script to copy existing charts from reports directory to dashboard static directory.
"""

import shutil
from pathlib import Path
from config.settings import settings

def copy_charts_to_dashboard():
    """Copy all chart files from reports to dashboard static directory."""
    reports_dir = Path(settings.output_dir)
    dashboard_static_dir = Path(settings.dashboard_static_dir)
    
    # Ensure dashboard static directory exists
    dashboard_static_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all image files in reports directory
    image_extensions = ["*.png", "*.jpg", "*.jpeg"]
    copied_count = 0
    
    for ext in image_extensions:
        for file_path in reports_dir.glob(ext):
            filename = file_path.name
            destination = dashboard_static_dir / filename
            
            # Copy file if it doesn't exist in destination or if source is newer
            if not destination.exists() or file_path.stat().st_mtime > destination.stat().st_mtime:
                shutil.copy2(file_path, destination)
                print(f"✅ Copied: {filename}")
                copied_count += 1
            else:
                print(f"⏭️  Skipped (already exists): {filename}")
    
    print(f"\n📊 Summary:")
    print(f"   - Source directory: {reports_dir}")
    print(f"   - Destination directory: {dashboard_static_dir}")
    print(f"   - Files copied: {copied_count}")
    
    # List files in dashboard static directory
    dashboard_files = list(dashboard_static_dir.glob("*.png")) + list(dashboard_static_dir.glob("*.jpg")) + list(dashboard_static_dir.glob("*.jpeg"))
    print(f"   - Total files in dashboard static: {len(dashboard_files)}")

if __name__ == "__main__":
    print("🔄 Copying charts to dashboard static directory...")
    copy_charts_to_dashboard()
    print("✅ Done!") 