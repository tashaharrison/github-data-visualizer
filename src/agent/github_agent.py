"""
Main AI agent for GitHub PR analytics using LangChain, OpenAI, and MCP.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger
from config.settings import settings
from src.mcp.github_client import GitHubMCPClient
from src.analysis.pr_analyzer import PRAnalyzer
from src.analysis.visualizer import PRVisualizer
from src.analysis.multi_repo_analyzer import MultiRepoAnalyzer
from src.analysis.multi_repo_visualizer import MultiRepoVisualizer
from src.utils import save_json_data, save_csv_data
from src.agent.prompts import create_analysis_messages
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


class GitHubPRAnalyzerAgent:
    """AI agent for analyzing GitHub PRs using MCP, LangChain, and OpenAI."""
    def __init__(self):
        self.client = GitHubMCPClient()
        self.analyzer = PRAnalyzer()
        self.visualizer = PRVisualizer()
        self.multi_repo_analyzer = MultiRepoAnalyzer()
        self.multi_repo_visualizer = MultiRepoVisualizer()
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.2,
            max_tokens=2048
        )

    def _get_repositories_to_analyze(self):
        """Get list of repositories to analyze."""
        repos = []
        
        # Check if multi-repository analysis is configured
        has_multi_repo_config = False
        if settings.repositories:
            try:
                if isinstance(settings.repositories, str):
                    repos_config = json.loads(settings.repositories)
                else:
                    repos_config = settings.repositories
                
                if repos_config and len(repos_config) > 0:
                    has_multi_repo_config = True
                    
                    for repo_config in repos_config:
                        if isinstance(repo_config, dict) and "owner" in repo_config and "name" in repo_config:
                            display_name = repo_config.get("display_name", f"{repo_config['owner']}/{repo_config['name']}")
                            repos.append({
                                "owner": repo_config["owner"],
                                "name": repo_config["name"],
                                "display_name": display_name
                            })
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Error parsing repositories configuration: {e}")
        
        # Only add single repository if multi-repo is not configured
        if not has_multi_repo_config and settings.repo_owner and settings.repo_name:
            repos.append({
                "owner": settings.repo_owner,
                "name": settings.repo_name,
                "display_name": f"{settings.repo_owner}/{settings.repo_name}"
            })
        
        return repos

    async def analyze_prs(self):
        """Analyze PRs from single or multiple repositories."""
        # Test MCP connection
        if not await self.client.test_connection():
            logger.error("Cannot connect to MCP server. Aborting analysis.")
            return None

        repositories = self._get_repositories_to_analyze()
        
        if len(repositories) == 1:
            # Single repository analysis
            repo = repositories[0]
            logger.info(f"Analyzing single repository: {repo['display_name']}")
            
            prs = await self.client.get_pull_requests(
                owner=repo["owner"],
                repo=repo["name"],
                state="all"
            )
            
            if not prs:
                logger.warning("No PRs found for analysis.")
                return None

            analysis_data = self.analyzer.analyze_pr_data(prs)
            return analysis_data
            
        elif len(repositories) > 1:
            # Multi-repository analysis
            logger.info(f"Analyzing {len(repositories)} repositories")
            
            repo_data = {}
            for repo in repositories:
                logger.info(f"Fetching PRs for {repo['display_name']}")
                prs = await self.client.get_pull_requests(
                    owner=repo["owner"],
                    repo=repo["name"],
                    state="all"
                )
                repo_data[repo["display_name"]] = prs
            
            # Analyze all repositories
            multi_repo_analysis = self.multi_repo_analyzer.analyze_multiple_repos(repo_data)
            return multi_repo_analysis
        else:
            logger.error("No repositories configured for analysis.")
            return None

    def _cleanup_existing_reports(self):
        """Delete existing reports and visualizations before generating new ones."""
        logger.info("Cleaning up existing reports and visualizations")
        
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
            for pattern in patterns_to_delete:
                for file_path in reports_dir.glob(pattern):
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted: {file_path.name}")
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {file_path.name}: {e}")
        
        # Clean up dashboard static directory
        if dashboard_static_dir.exists():
            for pattern in patterns_to_delete:
                for file_path in dashboard_static_dir.glob(pattern):
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted from dashboard: {file_path.name}")
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {file_path.name} from dashboard: {e}")
        
        logger.info(f"Cleanup completed. Deleted {deleted_count} files")
        return deleted_count

    async def generate_reports(self, analysis_data):
        if not analysis_data:
            logger.warning("No analysis data to report.")
            return

        # Clean up existing reports before generating new ones
        self._cleanup_existing_reports()

        # Check if this is multi-repository analysis
        is_multi_repo = "individual_analyses" in analysis_data
        
        if is_multi_repo:
            # Multi-repository analysis
            logger.info("Generating multi-repository reports")
            
            # Save multi-repo analysis data
            save_json_data(analysis_data, f"{settings.output_dir}/multi_repo_analysis_{settings.analysis_year}.json")
            
            # Generate comparative visualizations
            self.multi_repo_visualizer.create_comparative_visualizations(analysis_data)
            
            # Generate individual repository reports
            for repo_name, repo_analysis in analysis_data["individual_analyses"].items():
                # Save individual repo data
                safe_repo_name = repo_name.replace("/", "_").replace(" ", "_")
                save_json_data(repo_analysis, f"{settings.output_dir}/{safe_repo_name}_analysis_{settings.analysis_year}.json")
                
                # Generate individual visualizations
                self.visualizer.create_all_visualizations(repo_analysis)
            
            # Generate comparative LLM insights
            await self._generate_multi_repo_insights(analysis_data)
            
        else:
            # Single repository analysis
            logger.info("Generating single repository reports")
            
            # Save raw data
            save_json_data(analysis_data, f"{settings.output_dir}/pr_analysis_{settings.analysis_year}.json")
            if analysis_data.get("raw_data", {}).get("all_prs"):
                save_csv_data(analysis_data["raw_data"]["all_prs"], f"{settings.output_dir}/pr_raw_{settings.analysis_year}.csv")

            # Generate visualizations
            self.visualizer.create_all_visualizations(analysis_data)

            # Generate LLM insights
            await self._generate_llm_insights(analysis_data)

    async def _generate_llm_insights(self, analysis_data):
        # Monthly analysis
        messages = create_analysis_messages(analysis_data, prompt_type="monthly")
        monthly_insight = self.llm.invoke(messages)
        logger.info(f"Monthly Insights: {monthly_insight.content}")
        with open(f"{settings.output_dir}/monthly_insights_{settings.analysis_year}.txt", "w") as f:
            f.write(monthly_insight.content)

        # Overall analysis
        messages = create_analysis_messages(analysis_data, prompt_type="overall")
        overall_insight = self.llm.invoke(messages)
        logger.info(f"Overall Insights: {overall_insight.content}")
        with open(f"{settings.output_dir}/overall_insights_{settings.analysis_year}.txt", "w") as f:
            f.write(overall_insight.content)

    async def _generate_multi_repo_insights(self, analysis_data):
        """Generate insights for multi-repository analysis."""
        logger.info("Generating multi-repository insights")
        
        # Create a summary for LLM analysis
        summary_data = {
            "total_repositories": analysis_data["summary"]["total_repositories"],
            "total_prs_across_repos": analysis_data["summary"]["total_prs_across_repos"],
            "individual_analyses": {},
            "comparative_analysis": analysis_data.get("comparative_analysis", {}),
            "cross_repo_insights": analysis_data.get("cross_repo_insights", {})
        }
        
        # Add summary stats for each repository
        for repo_name, repo_analysis in analysis_data["individual_analyses"].items():
            summary_data["individual_analyses"][repo_name] = {
                "total_prs": repo_analysis["summary"]["total_prs"],
                "merge_rate": repo_analysis.get("overall_stats", {}).get("merge_rate", 0),
                "avg_comments": repo_analysis.get("overall_stats", {}).get("avg_comments", 0),
                "avg_time_to_merge": repo_analysis.get("lifecycle_stats", {}).get("avg_time_to_merge", 0)
            }
        
        # Generate comparative insights
        messages = [
            SystemMessage(content="You are an expert data analyst specializing in GitHub repository analytics. Analyze the comparative data across multiple repositories and provide insights about development patterns, team productivity, and code quality trends."),
            HumanMessage(content=f"Please analyze the following multi-repository GitHub PR data for 2025:\n\n{json.dumps(summary_data, indent=2)}")
        ]
        
        comparative_insight = self.llm.invoke(messages)
        logger.info(f"Comparative Insights: {comparative_insight.content}")
        with open(f"{settings.output_dir}/comparative_insights_{settings.analysis_year}.txt", "w") as f:
            f.write(comparative_insight.content) 