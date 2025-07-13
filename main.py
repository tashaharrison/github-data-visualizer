#!/usr/bin/env python3
"""
Main entry point for the GitHub PR Analytics AI Agent.

This script orchestrates the entire workflow:
1. Connects to GitHub via MCP server
2. Fetches PR data for 2025
3. Analyzes monthly patterns
4. Generates insights using OpenAI
5. Creates visualizations and reports
"""

import asyncio
import sys
import argparse
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from config.settings import settings
from src.agent.github_agent import GitHubPRAnalyzerAgent
from src.utils import setup_logging


async def main():
    """Main execution function."""
    try:
        # Setup logging
        setup_logging(settings.log_level)
        logger.info("Starting GitHub PR Analytics AI Agent")
        
        # Ensure directories exist
        settings.ensure_directories()
        
        # Initialize the agent
        agent = GitHubPRAnalyzerAgent()
        
        # Run the analysis
        logger.info(f"Analyzing PRs for {settings.analysis_year}")
        results = await agent.analyze_prs()
        
        # Generate reports
        logger.info("Generating reports and visualizations")
        await agent.generate_reports(results)
        
        logger.info("Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        sys.exit(1)


def main_with_cleanup():
    """Main function with optional cleanup."""
    parser = argparse.ArgumentParser(description="GitHub PR Analytics AI Agent")
    parser.add_argument(
        "--cleanup", 
        action="store_true", 
        help="Clean up existing reports before running analysis"
    )
    parser.add_argument(
        "--cleanup-only", 
        action="store_true", 
        help="Only clean up existing reports, don't run analysis"
    )
    
    args = parser.parse_args()
    
    if args.cleanup_only:
        # Run cleanup only
        from cleanup_reports import cleanup_reports
        print("🧹 Running cleanup only...")
        deleted_count = cleanup_reports()
        print(f"✅ Cleanup completed. Deleted {deleted_count} files")
        return
    
    if args.cleanup:
        # Run cleanup before analysis
        from cleanup_reports import cleanup_reports
        print("🧹 Cleaning up existing reports before analysis...")
        deleted_count = cleanup_reports()
        print(f"✅ Cleanup completed. Deleted {deleted_count} files")
        print("🚀 Starting analysis...")
    
    # Run the main analysis
    asyncio.run(main())


if __name__ == "__main__":
    main_with_cleanup() 