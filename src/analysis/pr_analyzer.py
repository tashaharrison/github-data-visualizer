"""
Pull Request data analysis and statistics calculation.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Tuple
from loguru import logger

from src.utils import group_by_month, calculate_monthly_stats, parse_github_date


class PRAnalyzer:
    """Analyzes pull request data and calculates statistics."""
    
    def __init__(self):
        self.monthly_data = {}
        self.overall_stats = {}
    
    def analyze_pr_data(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pull request data and return comprehensive statistics."""
        logger.info(f"Analyzing {len(prs)} pull requests")
        
        if not prs:
            logger.warning("No pull requests to analyze")
            return self._empty_analysis_result()
        
        # Group PRs by month
        self.monthly_data = group_by_month(prs, "created_at")
        
        # Calculate monthly statistics
        monthly_stats = calculate_monthly_stats(self.monthly_data)
        
        # Calculate overall statistics
        overall_stats = self._calculate_overall_stats(prs)
        
        # Calculate trends
        trends = self._calculate_trends(monthly_stats)
        
        # Calculate contributor statistics
        contributor_stats = self._calculate_contributor_stats(prs)
        
        # Calculate PR lifecycle statistics
        lifecycle_stats = self._calculate_lifecycle_stats(prs)
        
        return {
            "summary": {
                "total_prs": len(prs),
                "analysis_period": "2025",
                "months_analyzed": len(monthly_stats),
                "generated_at": datetime.now().isoformat()
            },
            "monthly_stats": monthly_stats,
            "overall_stats": overall_stats,
            "trends": trends,
            "contributor_stats": contributor_stats,
            "lifecycle_stats": lifecycle_stats,
            "raw_data": {
                "prs_by_month": self.monthly_data,
                "all_prs": prs
            }
        }
    
    def _calculate_overall_stats(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall statistics for all PRs."""
        total_prs = len(prs)
        if total_prs == 0:
            return {}
        
        # State distribution
        states = {}
        for pr in prs:
            state = pr.get("state", "unknown")
            states[state] = states.get(state, 0) + 1
        
        # Merged vs closed
        merged_count = len([pr for pr in prs if pr.get("merged_at")])
        closed_not_merged = len([pr for pr in prs if pr.get("state") == "closed" and not pr.get("merged_at")])
        
        # Average metrics
        total_comments = sum(pr.get("comments", 0) for pr in prs)
        total_review_comments = sum(pr.get("review_comments", 0) for pr in prs)
        total_commits = sum(pr.get("commits", 0) for pr in prs)
        total_additions = sum(pr.get("additions", 0) for pr in prs)
        total_deletions = sum(pr.get("deletions", 0) for pr in prs)
        
        return {
            "total_prs": total_prs,
            "state_distribution": states,
            "merged_count": merged_count,
            "closed_not_merged_count": closed_not_merged,
            "merge_rate": (merged_count / total_prs) * 100 if total_prs > 0 else 0,
            "avg_comments": total_comments / total_prs if total_prs > 0 else 0,
            "avg_review_comments": total_review_comments / total_prs if total_prs > 0 else 0,
            "avg_commits": total_commits / total_prs if total_prs > 0 else 0,
            "avg_additions": total_additions / total_prs if total_prs > 0 else 0,
            "avg_deletions": total_deletions / total_prs if total_prs > 0 else 0,
            "total_changes": total_additions + total_deletions
        }
    
    def _calculate_trends(self, monthly_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends from monthly statistics."""
        if len(monthly_stats) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame.from_dict(monthly_stats, orient='index')
        df.index = pd.to_datetime(df.index + "-01")
        df = df.sort_index()
        
        trends = {}
        
        # Linear trend for PR count
        if len(df) > 1:
            x = range(len(df))
            y = df['count'].values
            slope = (y[-1] - y[0]) / len(df) if len(df) > 1 else 0
            trends["pr_count_trend"] = {
                "slope": slope,
                "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "change_rate": slope
            }
        
        # Monthly averages
        trends["monthly_averages"] = {
            "avg_prs_per_month": df['count'].mean(),
            "avg_merge_rate": df['merged_count'].sum() / df['count'].sum() * 100 if df['count'].sum() > 0 else 0,
            "avg_comments_per_pr": df['avg_comments'].mean()
        }
        
        # Peak months
        max_month = df['count'].idxmax()
        trends["peak_activity"] = {
            "peak_month": max_month.strftime("%Y-%m"),
            "peak_count": int(df['count'].max())
        }
        
        return trends
    
    def _calculate_contributor_stats(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about PR contributors."""
        contributors = {}
        
        for pr in prs:
            user = pr.get("user", {})
            username = user.get("login", "unknown")
            
            if username not in contributors:
                contributors[username] = {
                    "pr_count": 0,
                    "merged_count": 0,
                    "total_comments": 0,
                    "total_review_comments": 0,
                    "total_additions": 0,
                    "total_deletions": 0
                }
            
            contributors[username]["pr_count"] += 1
            if pr.get("merged_at"):
                contributors[username]["merged_count"] += 1
            
            contributors[username]["total_comments"] += pr.get("comments", 0)
            contributors[username]["total_review_comments"] += pr.get("review_comments", 0)
            contributors[username]["total_additions"] += pr.get("additions", 0)
            contributors[username]["total_deletions"] += pr.get("deletions", 0)
        
        # Sort by PR count
        sorted_contributors = sorted(
            contributors.items(), 
            key=lambda x: x[1]["pr_count"], 
            reverse=True
        )
        
        return {
            "total_contributors": len(contributors),
            "top_contributors": sorted_contributors[:10],
            "contributor_details": contributors
        }
    
    def _calculate_lifecycle_stats(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate PR lifecycle statistics."""
        lifecycle_data = []
        
        for pr in prs:
            created_at = parse_github_date(pr["created_at"])
            closed_at = None
            merged_at = None
            
            if pr.get("closed_at"):
                closed_at = parse_github_date(pr["closed_at"])
            
            if pr.get("merged_at"):
                merged_at = parse_github_date(pr["merged_at"])
            
            lifecycle = {
                "pr_number": pr["number"],
                "created_at": created_at,
                "closed_at": closed_at,
                "merged_at": merged_at,
                "state": pr.get("state"),
                "is_merged": bool(merged_at)
            }
            
            # Calculate time to close/merge
            if closed_at:
                lifecycle["time_to_close"] = (closed_at - created_at).total_seconds() / 3600  # hours
            
            if merged_at:
                lifecycle["time_to_merge"] = (merged_at - created_at).total_seconds() / 3600  # hours
            
            lifecycle_data.append(lifecycle)
        
        # Calculate averages
        closed_prs = [pr for pr in lifecycle_data if pr.get("time_to_close")]
        merged_prs = [pr for pr in lifecycle_data if pr.get("time_to_merge")]
        
        return {
            "total_prs": len(lifecycle_data),
            "closed_prs": len(closed_prs),
            "merged_prs": len(merged_prs),
            "avg_time_to_close": sum(pr["time_to_close"] for pr in closed_prs) / len(closed_prs) if closed_prs else 0,
            "avg_time_to_merge": sum(pr["time_to_merge"] for pr in merged_prs) / len(merged_prs) if merged_prs else 0,
            "lifecycle_details": lifecycle_data
        }
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result structure."""
        return {
            "summary": {
                "total_prs": 0,
                "analysis_period": "2025",
                "months_analyzed": 0,
                "generated_at": datetime.now().isoformat()
            },
            "monthly_stats": {},
            "overall_stats": {},
            "trends": {"message": "No data available"},
            "contributor_stats": {"total_contributors": 0, "top_contributors": []},
            "lifecycle_stats": {"total_prs": 0},
            "raw_data": {"prs_by_month": {}, "all_prs": []}
        } 