#!/usr/bin/env python3
"""
Script to clean up existing reports and visualizations.
"""

import sys
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from config.settings import settings


def cleanup_reports():
    """Clean up existing reports and visualizations."""
    logger.info("Starting cleanup of existing reports and visualizations")
    
    reports_dir = Path(settings.output_dir)
    dashboard_static_dir = Path(settings.dashboard_static_dir)
    
    # Files to delete patterns
    patterns_to_delete = [
        "*_analysis_*.json",
        "*_insights_*.txt",
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.csv"
    ]
    
    deleted_count = 0
    
    # Clean up reports directory
    if reports_dir.exists():
        logger.info(f"Cleaning up reports directory: {reports_dir}")
        for pattern in patterns_to_delete:
            for file_path in reports_dir.glob(pattern):
                try:
                    file_path.unlink()
                    logger.info(f"Deleted: {file_path.name}")
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete {file_path.name}: {e}")
    else:
        logger.warning(f"Reports directory does not exist: {reports_dir}")
    
    # Clean up dashboard static directory
    if dashboard_static_dir.exists():
        logger.info(f"Cleaning up dashboard static directory: {dashboard_static_dir}")
        for pattern in patterns_to_delete:
            for file_path in dashboard_static_dir.glob(pattern):
                try:
                    file_path.unlink()
                    logger.info(f"Deleted from dashboard: {file_path.name}")
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete {file_path.name} from dashboard: {e}")
    else:
        logger.warning(f"Dashboard static directory does not exist: {dashboard_static_dir}")
    
    logger.info(f"Cleanup completed. Deleted {deleted_count} files")
    return deleted_count


def main():
    """Main function."""
    try:
        # Setup logging
        logger.add("logs/cleanup.log", rotation="1 day", retention="30 days")
        
        # Ensure directories exist
        settings.ensure_directories()
        
        print("🧹 Starting Report Cleanup")
        print("=" * 40)
        
        deleted_count = cleanup_reports()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"📊 Files deleted: {deleted_count}")
        
        if deleted_count == 0:
            print("ℹ️  No files were found to delete")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 