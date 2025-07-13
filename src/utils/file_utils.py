"""
File I/O utility functions for the GitHub PR Analytics AI Agent.
"""

import json
import csv
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger


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


def ensure_directory(path: str) -> None:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True) 