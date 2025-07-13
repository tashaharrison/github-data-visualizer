"""
Multi-repository PR analysis and comparison.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Tuple
from loguru import logger

from src.analysis.pr_analyzer import PRAnalyzer
from src.utils import parse_github_date


class MultiRepoAnalyzer:
    """Analyzes and compares PR data across multiple repositories."""
    
    def __init__(self):
        self.analyzer = PRAnalyzer()
        self.repo_analyses = {}
        self.comparative_stats = {}
    
    def analyze_multiple_repos(self, repo_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze multiple repositories and provide comparative analysis."""
        logger.info(f"Analyzing {len(repo_data)} repositories")
        
        # Analyze each repository individually
        for repo_name, prs in repo_data.items():
            logger.info(f"Analyzing repository: {repo_name}")
            self.repo_analyses[repo_name] = self.analyzer.analyze_pr_data(prs)
        
        # Generate comparative analysis
        comparative_analysis = self._generate_comparative_analysis()
        
        # Generate cross-repository insights
        cross_repo_insights = self._generate_cross_repo_insights()
        
        # Calculate months analyzed from individual analyses
        months_analyzed = 0
        for analysis in self.repo_analyses.values():
            if analysis.get("summary", {}).get("months_analyzed"):
                months_analyzed = max(months_analyzed, analysis["summary"]["months_analyzed"])
        
        return {
            "individual_analyses": self.repo_analyses,
            "comparative_analysis": comparative_analysis,
            "cross_repo_insights": cross_repo_insights,
            "summary": {
                "total_repositories": len(repo_data),
                "total_prs_across_repos": sum(
                    analysis["summary"]["total_prs"] 
                    for analysis in self.repo_analyses.values()
                ),
                "months_analyzed": months_analyzed,
                "analysis_period": "2025",
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _generate_comparative_analysis(self) -> Dict[str, Any]:
        """Generate comparative statistics across repositories."""
        if len(self.repo_analyses) < 2:
            return {"message": "Need at least 2 repositories for comparative analysis"}
        
        comparative_stats = {
            "repository_rankings": {},
            "activity_comparison": {},
            "quality_metrics": {},
            "trend_comparison": {}
        }
        
        # Repository rankings by various metrics
        repos = list(self.repo_analyses.keys())
        
        # PR count ranking
        pr_counts = {repo: analysis["summary"]["total_prs"] for repo, analysis in self.repo_analyses.items()}
        comparative_stats["repository_rankings"]["by_pr_count"] = sorted(
            pr_counts.items(), key=lambda x: x[1], reverse=True
        )
        
        # Merge rate ranking
        merge_rates = {}
        for repo, analysis in self.repo_analyses.items():
            overall_stats = analysis.get("overall_stats", {})
            if overall_stats.get("total_prs", 0) > 0:
                merge_rates[repo] = overall_stats.get("merge_rate", 0)
        
        comparative_stats["repository_rankings"]["by_merge_rate"] = sorted(
            merge_rates.items(), key=lambda x: x[1], reverse=True
        )
        
        # Average comments ranking
        avg_comments = {}
        for repo, analysis in self.repo_analyses.items():
            overall_stats = analysis.get("overall_stats", {})
            avg_comments[repo] = overall_stats.get("avg_comments", 0)
        
        comparative_stats["repository_rankings"]["by_avg_comments"] = sorted(
            avg_comments.items(), key=lambda x: x[1], reverse=True
        )
        
        # Activity comparison
        monthly_activity = {}
        for repo, analysis in self.repo_analyses.items():
            monthly_stats = analysis.get("monthly_stats", {})
            total_monthly_prs = sum(stats["count"] for stats in monthly_stats.values())
            monthly_activity[repo] = {
                "total_prs": total_monthly_prs,
                "avg_prs_per_month": total_monthly_prs / len(monthly_stats) if monthly_stats else 0,
                "peak_month": max(monthly_stats.items(), key=lambda x: x[1]["count"])[0] if monthly_stats else None,
                "peak_count": max(stats["count"] for stats in monthly_stats.values()) if monthly_stats else 0
            }
        
        comparative_stats["activity_comparison"] = monthly_activity
        
        # Quality metrics comparison
        quality_metrics = {}
        for repo, analysis in self.repo_analyses.items():
            overall_stats = analysis.get("overall_stats", {})
            lifecycle_stats = analysis.get("lifecycle_stats", {})
            
            quality_metrics[repo] = {
                "merge_rate": overall_stats.get("merge_rate", 0),
                "avg_time_to_merge": lifecycle_stats.get("avg_time_to_merge", 0),
                "avg_comments": overall_stats.get("avg_comments", 0),
                "avg_review_comments": overall_stats.get("avg_review_comments", 0),
                "total_changes": overall_stats.get("total_changes", 0)
            }
        
        comparative_stats["quality_metrics"] = quality_metrics
        
        return comparative_stats
    
    def _generate_cross_repo_insights(self) -> Dict[str, Any]:
        """Generate insights that span across repositories."""
        if len(self.repo_analyses) < 2:
            return {"message": "Need at least 2 repositories for cross-repo insights"}
        
        insights = {
            "most_active_repo": None,
            "highest_quality_repo": None,
            "fastest_processing_repo": None,
            "most_engaged_community": None,
            "consistency_analysis": {},
            "collaboration_patterns": {}
        }
        
        # Find most active repository
        total_prs = {repo: analysis["summary"]["total_prs"] for repo, analysis in self.repo_analyses.items()}
        insights["most_active_repo"] = max(total_prs.items(), key=lambda x: x[1])
        
        # Find highest quality repository (based on merge rate and review engagement)
        quality_scores = {}
        for repo, analysis in self.repo_analyses.items():
            overall_stats = analysis.get("overall_stats", {})
            merge_rate = overall_stats.get("merge_rate", 0)
            avg_comments = overall_stats.get("avg_comments", 0)
            avg_review_comments = overall_stats.get("avg_review_comments", 0)
            
            # Simple quality score: merge rate + normalized engagement
            quality_score = merge_rate + (avg_comments + avg_review_comments) * 10
            quality_scores[repo] = quality_score
        
        insights["highest_quality_repo"] = max(quality_scores.items(), key=lambda x: x[1])
        
        # Find fastest processing repository
        processing_times = {}
        for repo, analysis in self.repo_analyses.items():
            lifecycle_stats = analysis.get("lifecycle_stats", {})
            avg_time_to_merge = lifecycle_stats.get("avg_time_to_merge", float('inf'))
            if avg_time_to_merge < float('inf'):
                processing_times[repo] = avg_time_to_merge
        
        if processing_times:
            insights["fastest_processing_repo"] = min(processing_times.items(), key=lambda x: x[1])
        
        # Find most engaged community (highest average comments)
        engagement_scores = {}
        for repo, analysis in self.repo_analyses.items():
            overall_stats = analysis.get("overall_stats", {})
            avg_comments = overall_stats.get("avg_comments", 0)
            avg_review_comments = overall_stats.get("avg_review_comments", 0)
            engagement_scores[repo] = avg_comments + avg_review_comments
        
        insights["most_engaged_community"] = max(engagement_scores.items(), key=lambda x: x[1])
        
        # Consistency analysis
        consistency_analysis = {}
        for repo, analysis in self.repo_analyses.items():
            monthly_stats = analysis.get("monthly_stats", {})
            if monthly_stats:
                pr_counts = [stats["count"] for stats in monthly_stats.values()]
                consistency_analysis[repo] = {
                    "std_dev": pd.Series(pr_counts).std(),
                    "coefficient_of_variation": pd.Series(pr_counts).std() / pd.Series(pr_counts).mean() if pd.Series(pr_counts).mean() > 0 else 0,
                    "min_monthly_prs": min(pr_counts),
                    "max_monthly_prs": max(pr_counts)
                }
        
        insights["consistency_analysis"] = consistency_analysis
        
        return insights
    
    def get_repository_summary_table(self) -> pd.DataFrame:
        """Create a summary table comparing all repositories."""
        if not self.repo_analyses:
            return pd.DataFrame()
        
        summary_data = []
        for repo_name, analysis in self.repo_analyses.items():
            overall_stats = analysis.get("overall_stats", {})
            lifecycle_stats = analysis.get("lifecycle_stats", {})
            contributor_stats = analysis.get("contributor_stats", {})
            
            summary_data.append({
                "Repository": repo_name,
                "Total PRs": overall_stats.get("total_prs", 0),
                "Merge Rate (%)": round(overall_stats.get("merge_rate", 0), 2),
                "Avg Comments": round(overall_stats.get("avg_comments", 0), 2),
                "Avg Review Comments": round(overall_stats.get("avg_review_comments", 0), 2),
                "Avg Time to Merge (hours)": round(lifecycle_stats.get("avg_time_to_merge", 0), 2),
                "Total Contributors": contributor_stats.get("total_contributors", 0),
                "Total Changes": overall_stats.get("total_changes", 0)
            })
        
        return pd.DataFrame(summary_data) 