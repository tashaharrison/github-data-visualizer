"""
Multi-repository data visualization for PR analysis.
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


class MultiRepoVisualizer:
    """Generates visualizations for multi-repository PR analysis."""
    
    def __init__(self):
        self.output_dir = Path(settings.output_dir)
        self.dashboard_static_dir = Path(settings.dashboard_static_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.dashboard_static_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_comparative_visualizations(self, multi_repo_analysis: Dict[str, Any]) -> List[str]:
        """Create comparative visualizations across repositories."""
        logger.info("Creating multi-repository visualizations")
        
        saved_files = []
        
        # Repository comparison chart
        if multi_repo_analysis.get("individual_analyses"):
            comparison_file = self._create_repository_comparison_chart(multi_repo_analysis)
            saved_files.append(comparison_file)
        
        # Quality metrics radar chart
        if multi_repo_analysis.get("comparative_analysis", {}).get("quality_metrics"):
            radar_file = self._create_quality_radar_chart(multi_repo_analysis["comparative_analysis"]["quality_metrics"])
            saved_files.append(radar_file)
        
        # Activity heatmap across repositories
        if multi_repo_analysis.get("individual_analyses"):
            heatmap_file = self._create_cross_repo_activity_heatmap(multi_repo_analysis["individual_analyses"])
            saved_files.append(heatmap_file)
        
        # Merge rate comparison
        if multi_repo_analysis.get("comparative_analysis", {}).get("quality_metrics"):
            merge_file = self._create_merge_rate_comparison(multi_repo_analysis["comparative_analysis"]["quality_metrics"])
            saved_files.append(merge_file)
        
        # Processing time comparison
        if multi_repo_analysis.get("comparative_analysis", {}).get("quality_metrics"):
            time_file = self._create_processing_time_comparison(multi_repo_analysis["comparative_analysis"]["quality_metrics"])
            saved_files.append(time_file)
        
        logger.info(f"Created {len(saved_files)} multi-repository visualizations")
        return saved_files
    
    def _create_repository_comparison_chart(self, multi_repo_analysis: Dict[str, Any]) -> str:
        """Create a bar chart comparing repositories by total PRs."""
        individual_analyses = multi_repo_analysis.get("individual_analyses", {})
        
        repos = list(individual_analyses.keys())
        total_prs = [analysis["summary"]["total_prs"] for analysis in individual_analyses.values()]
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(repos, total_prs, color='lightblue', alpha=0.7)
        
        # Add value labels on bars
        for bar, count in zip(bars, total_prs):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom')
        
        plt.title('Total Pull Requests by Repository (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Repository', fontsize=12)
        plt.ylabel('Number of PRs', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = self.output_dir / f"repository_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created repository comparison chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        
        return str(filename)
    
    def _create_quality_radar_chart(self, quality_metrics: Dict[str, Dict[str, float]]) -> str:
        """Create a radar chart comparing quality metrics across repositories."""
        if len(quality_metrics) < 2:
            return ""
        
        # Prepare data for radar chart
        metrics = ['merge_rate', 'avg_comments', 'avg_review_comments']
        repos = list(quality_metrics.keys())
        
        # Normalize data for radar chart (0-1 scale)
        normalized_data = {}
        for repo, metrics_data in quality_metrics.items():
            normalized_data[repo] = {}
            for metric in metrics:
                value = metrics_data.get(metric, 0)
                # Simple normalization - could be improved
                if metric == 'merge_rate':
                    normalized_data[repo][metric] = min(value / 100, 1.0)
                else:
                    normalized_data[repo][metric] = min(value / 10, 1.0)  # Cap at 10
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        for repo in repos:
            values = [normalized_data[repo].get(metric, 0) for metric in metrics]
            values += values[:1]  # Complete the circle
            ax.plot(angles, values, 'o-', linewidth=2, label=repo)
            ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([metric.replace('_', ' ').title() for metric in metrics])
        ax.set_ylim(0, 1)
        ax.set_title('Repository Quality Metrics Comparison (2025)', fontsize=16, fontweight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        filename = self.output_dir / f"quality_radar_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created quality radar chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_cross_repo_activity_heatmap(self, individual_analyses: Dict[str, Dict[str, Any]]) -> str:
        """Create a heatmap showing monthly activity across repositories."""
        # Prepare data for heatmap
        all_months = set()
        for analysis in individual_analyses.values():
            monthly_stats = analysis.get("monthly_stats", {})
            all_months.update(monthly_stats.keys())
        
        all_months = sorted(list(all_months))
        repos = list(individual_analyses.keys())
        
        # Create heatmap data
        heatmap_data = []
        for repo in repos:
            monthly_stats = individual_analyses[repo].get("monthly_stats", {})
            row = [monthly_stats.get(month, {}).get("count", 0) for month in all_months]
            heatmap_data.append(row)
        
        plt.figure(figsize=(15, 8))
        sns.heatmap(heatmap_data, 
                   xticklabels=all_months,
                   yticklabels=repos,
                   annot=True, 
                   fmt='d',
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Number of PRs'})
        
        plt.title('Monthly PR Activity Across Repositories (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Repository', fontsize=12)
        plt.tight_layout()
        
        filename = self.output_dir / f"cross_repo_activity_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created cross-repo activity heatmap: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_merge_rate_comparison(self, quality_metrics: Dict[str, Dict[str, float]]) -> str:
        """Create a bar chart comparing merge rates across repositories."""
        repos = list(quality_metrics.keys())
        merge_rates = [metrics.get("merge_rate", 0) for metrics in quality_metrics.values()]
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(repos, merge_rates, color='lightgreen', alpha=0.7)
        
        # Add value labels on bars
        for bar, rate in zip(bars, merge_rates):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{rate:.1f}%", ha='center', va='bottom')
        
        plt.title('Merge Rate Comparison Across Repositories (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Repository', fontsize=12)
        plt.ylabel('Merge Rate (%)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = self.output_dir / f"merge_rate_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created merge rate comparison chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename)
    
    def _create_processing_time_comparison(self, quality_metrics: Dict[str, Dict[str, float]]) -> str:
        """Create a bar chart comparing processing times across repositories."""
        repos = list(quality_metrics.keys())
        processing_times = [metrics.get("avg_time_to_merge", 0) for metrics in quality_metrics.values()]
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(repos, processing_times, color='lightcoral', alpha=0.7)
        
        # Add value labels on bars
        for bar, time in zip(bars, processing_times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{time:.1f}h", ha='center', va='bottom')
        
        plt.title('Average Time to Merge Comparison (2025)', fontsize=16, fontweight='bold')
        plt.xlabel('Repository', fontsize=12)
        plt.ylabel('Time to Merge (hours)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = self.output_dir / f"processing_time_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save to dashboard static directory
        dashboard_filename = self.dashboard_static_dir / filename.name
        plt.savefig(dashboard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        logger.info(f"Created processing time comparison chart: {filename}")
        logger.info(f"Saved to dashboard static: {dashboard_filename}")
        return str(filename) 