"""
Data processing utility functions for the GitHub PR Analytics AI Agent.
"""

from typing import Any, Dict, List
from .date_utils import parse_github_date


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