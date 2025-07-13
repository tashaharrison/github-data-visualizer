"""
Utility helper functions for the GitHub PR Analytics AI Agent.
"""

import json
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/agent.log",
        rotation="1 day",
        retention="30 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )


def save_json_data(data: Dict[str, Any], filepath: str) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"Data saved to {filepath}")


def save_csv_data(data: List[Dict[str, Any]], filepath: str) -> None:
    """Save data to CSV file."""
    if not data:
        logger.warning("No data to save to CSV")
        return
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Data saved to {filepath}")


def format_date(date: datetime) -> str:
    """Format datetime to string."""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def parse_github_date(date_str: str) -> datetime:
    """Parse GitHub API date string to datetime."""
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


def group_by_month(data: List[Dict[str, Any]], date_field: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group data by month."""
    grouped = {}
    for item in data:
        date = parse_github_date(item[date_field])
        month_key = date.strftime("%Y-%m")
        if month_key not in grouped:
            grouped[month_key] = []
        grouped[month_key].append(item)
    return grouped


def calculate_monthly_stats(grouped_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """Calculate monthly statistics."""
    stats = {}
    for month, items in grouped_data.items():
        stats[month] = {
            "count": len(items),
            "open_count": len([item for item in items if item.get("state") == "open"]),
            "closed_count": len([item for item in items if item.get("state") == "closed"]),
            "merged_count": len([item for item in items if item.get("merged_at")]),
            "avg_comments": sum(item.get("comments", 0) for item in items) / len(items) if items else 0,
            "avg_reviews": sum(item.get("review_comments", 0) for item in items) / len(items) if items else 0
        }
    return stats


def ensure_directory(path: str) -> None:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S") 