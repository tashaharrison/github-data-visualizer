"""
Date and time utility functions for the GitHub PR Analytics AI Agent.
"""

from datetime import datetime


def format_date(date: datetime) -> str:
    """Format datetime to string."""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def parse_github_date(date_str: str) -> datetime:
    """Parse GitHub API date string to datetime."""
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S") 