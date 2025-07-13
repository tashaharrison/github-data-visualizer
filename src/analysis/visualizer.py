"""
Data visualization for PR analysis results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger

from config.settings import settings


class PRVisualizer:
    """Generates visualizations for PR analysis data."""
    
    def __init__(self):
        self.output_dir = Path(settings.output_dir)
        self.dashboard_static_dir = Path(settings.dashboard_static_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.dashboard_static_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_all_visualizations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Create all visualizations and return list of saved file paths."""
        logger.info("Creating visualizations")
        
        saved_files = []
        
        # Monthly PR count chart
        if analysis_data.get("monthly_stats"):
            monthly_file = self._create_monthly_pr_chart(analysis_data["monthly_stats"])
            saved_files.append(monthly_file)
        
        # PR state distribution pie chart
        if analysis_data.get("overall_stats", {}).get("state_distribution"):
            state_file = self._create_state_distribution_chart(analysis_data["overall_stats"]["state_distribution"])
            saved_files.append(state_file)
        
        # Contributor activity chart
        if analysis_data.get("contributor_stats", {}).get("top_contributors"):
            contributor_file = self._create_contributor_chart(analysis_data["contributor_stats"]["top_contributors"])
            saved_files.append(contributor_file)
        
        # PR lifecycle timeline
        if analysis_data.get("lifecycle_stats", {}).get("lifecycle_details"):
            lifecycle_file = self._create_lifecycle_chart(analysis_data["lifecycle_stats"]["lifecycle_details"])
            saved_files.append(lifecycle_file)
        
        # Trends chart
        if analysis_data.get("trends") and not isinstance(analysis_data["trends"], dict):
            trends_file = self._create_trends_chart(analysis_data["monthly_stats"])
            saved_files.append(trends_file)
        
        # Activity heatmap
        if analysis_data.get("monthly_stats"):
            heatmap_file = self._create_activity_heatmap(analysis_data["monthly_stats"])
            saved_files.append(heatmap_file)
        
        logger.info(f"Created {len(saved_files)} visualizations")
        return saved_files
    
    def _create_monthly_pr_chart(self, monthly_stats: Dict[str, Dict[str, Any]]) -> str:
        """Create monthly PR count chart."""
        months = list(monthly_stats.keys())
        counts = [stats["count"] for stats in monthly_stats.values()]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(months, counts, color='skyblue', alpha=0.7)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom')
        
        plt.title('Pull Requests Created by Month (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Number of PRs', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = self.output_dir / f"monthly_pr_count_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created monthly PR chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_state_distribution_chart(self, state_distribution: Dict[str, int]) -> str:
        """Create PR state distribution pie chart."""
        if not state_distribution:
            return ""
        
        states = list(state_distribution.keys())
        counts = list(state_distribution.values())
        
        plt.figure(figsize=(10, 8))
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        
        wedges, texts, autotexts = plt.pie(counts, labels=states, autopct='%1.1f%%',
                                          colors=colors[:len(states)], startangle=90)
        
        plt.title('Pull Request State Distribution (2025)', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        filename = self.output_dir / f"pr_state_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created state distribution chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_contributor_chart(self, top_contributors: List[tuple]) -> str:
        """Create top contributors bar chart."""
        if not top_contributors:
            return ""
        
        # Take top 10 contributors
        contributors = top_contributors[:10]
        usernames = [contrib[0] for contrib in contributors]
        pr_counts = [contrib[1]["pr_count"] for contrib in contributors]
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(usernames, pr_counts, color='lightcoral', alpha=0.7)
        
        # Add value labels
        for bar, count in zip(bars, pr_counts):
            plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(count), ha='left', va='center')
        
        plt.title('Top Contributors by PR Count (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Number of PRs', fontsize=12)
        plt.ylabel('Contributor', fontsize=12)
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        filename = self.output_dir / f"top_contributors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created contributor chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_lifecycle_chart(self, lifecycle_details: List[Dict[str, Any]]) -> str:
        """Create PR lifecycle timeline chart."""
        if not lifecycle_details:
            return ""
        
        # Filter for closed/merged PRs
        closed_prs = [pr for pr in lifecycle_details if pr.get("time_to_close")]
        merged_prs = [pr for pr in lifecycle_details if pr.get("time_to_merge")]
        
        plt.figure(figsize=(12, 6))
        
        if closed_prs:
            close_times = [pr["time_to_close"] for pr in closed_prs]
            plt.hist(close_times, bins=20, alpha=0.7, label='Time to Close', color='orange')
        
        if merged_prs:
            merge_times = [pr["time_to_merge"] for pr in merged_prs]
            plt.hist(merge_times, bins=20, alpha=0.7, label='Time to Merge', color='green')
        
        plt.title('PR Lifecycle Timeline Distribution (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Time (hours)', fontsize=12)
        plt.ylabel('Number of PRs', fontsize=12)
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filename = self.output_dir / f"pr_lifecycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created lifecycle chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_trends_chart(self, monthly_stats: Dict[str, Dict[str, Any]]) -> str:
        """Create trends line chart."""
        if len(monthly_stats) < 2:
            return ""
        
        months = list(monthly_stats.keys())
        counts = [stats["count"] for stats in monthly_stats.values()]
        
        plt.figure(figsize=(12, 6))
        plt.plot(months, counts, marker='o', linewidth=2, markersize=8, color='blue')
        
        # Add trend line
        x = range(len(months))
        z = np.polyfit(x, counts, 1)
        p = np.poly1d(z)
        plt.plot(months, p(x), "r--", alpha=0.8, label=f'Trend line')
        
        plt.title('PR Creation Trends (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Number of PRs', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        filename = self.output_dir / f"pr_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created trends chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_activity_heatmap(self, monthly_stats: Dict[str, Dict[str, Any]]) -> str:
        """Create activity heatmap."""
        if not monthly_stats:
            return ""
        
        # Prepare data for heatmap
        months = list(monthly_stats.keys())
        metrics = ['count', 'merged_count', 'avg_comments', 'avg_reviews']
        
        heatmap_data = []
        for metric in metrics:
            row = [monthly_stats[month].get(metric, 0) for month in months]
            heatmap_data.append(row)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, 
                   xticklabels=months,
                   yticklabels=metrics,
                   annot=True, 
                   fmt='.1f',
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Value'})
        
        plt.title('Monthly PR Activity Heatmap (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Metric', fontsize=12)
        plt.tight_layout()
        
        filename = self.output_dir / f"activity_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created activity heatmap: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename) 