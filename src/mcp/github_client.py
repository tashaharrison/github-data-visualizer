"""
GitHub MCP client for fetching pull request data.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from config.settings import settings


class GitHubMCPClient:
    """Client for interacting with GitHub via MCP server."""
    
    def __init__(self):
        self.base_url = settings.mcp_server_url
        self.headers = {
            "Authorization": f"Bearer {settings.mcp_server_token}" if settings.mcp_server_token else "",
            "Content-Type": "application/json"
        }
        self.timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to MCP server."""
        url = f"{self.base_url}{endpoint}"
        
        # For remote MCP server, we need to use the GitHub API directly
        if "fly.dev" in self.base_url:
            # Use GitHub API directly with the token
            github_url = f"https://api.github.com{endpoint}"
            headers = {
                "Authorization": f"token {settings.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                try:
                    async with session.get(github_url, headers=headers, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                except aiohttp.ClientError as e:
                    logger.error(f"Error making request to {github_url}: {e}")
                    raise
        else:
            # Use local MCP server
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                try:
                    async with session.get(url, headers=self.headers, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                except aiohttp.ClientError as e:
                    logger.error(f"Error making request to {url}: {e}")
                    raise
    
    async def get_pull_requests(self, 
                               owner: str, 
                               repo: str, 
                               state: str = "all",
                               per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch pull requests from GitHub repository with pagination."""
        logger.info(f"Fetching PRs for {owner}/{repo}")
        
        all_prs = []
        page = 1
        
        # Filter PRs for 2025
        start_date, end_date = settings.get_analysis_date_range()
        
        while True:
            params = {
                "state": state,
                "per_page": per_page,
                "page": page,
                "sort": "created",
                "direction": "desc"
            }
            
            endpoint = f"/repos/{owner}/{repo}/pulls"
            response = await self._make_request(endpoint, params)
            
            # If no more PRs, break
            if not response:
                break
            
            # Filter PRs for 2025
            for pr in response:
                created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                if start_date <= created_at <= end_date:
                    all_prs.append(pr)
                # If we've gone past our date range, we can stop
                elif created_at < start_date:
                    break
            
            # If we've gone past our date range or no more pages, break
            if not response or len(response) < per_page:
                break
                
            page += 1
        
        logger.info(f"Found {len(all_prs)} PRs created in 2025")
        return all_prs
    
    async def get_pull_request_details(self, 
                                     owner: str, 
                                     repo: str, 
                                     pr_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return await self._make_request(endpoint)
    
    async def get_pull_request_reviews(self, 
                                     owner: str, 
                                     repo: str, 
                                     pr_number: int) -> List[Dict[str, Any]]:
        """Get reviews for a specific pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return await self._make_request(endpoint)
    
    async def get_pull_request_comments(self, 
                                      owner: str, 
                                      repo: str, 
                                      pr_number: int) -> List[Dict[str, Any]]:
        """Get comments for a specific pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        return await self._make_request(endpoint)
    
    async def get_repository_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository statistics."""
        endpoint = f"/repos/{owner}/{repo}"
        return await self._make_request(endpoint)
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information."""
        endpoint = f"/users/{username}"
        return await self._make_request(endpoint)
    
    async def test_connection(self) -> bool:
        """Test connection to MCP server."""
        try:
            # Try to get repository info as a connection test
            await self.get_repository_stats(settings.repo_owner, settings.repo_name)
            logger.info("Successfully connected to GitHub MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to GitHub MCP server: {e}")
            return False 