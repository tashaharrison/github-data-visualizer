"""
Configuration settings for the GitHub PR Analytics AI Agent.
"""
import os
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # GitHub Configuration
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_api_url: str = Field(default="https://api.github.com", env="GITHUB_API_URL")
    
    # MCP Server Configuration
    mcp_server_url: str = Field(default="https://mcp-server-github.fly.dev", env="MCP_SERVER_URL")
    mcp_server_token: Optional[str] = Field(default=None, env="MCP_SERVER_TOKEN")
    
    # Repository Configuration
    repo_owner: str = Field(..., env="REPO_OWNER")
    repo_name: str = Field(..., env="REPO_NAME")
    
    # Multi-repository Configuration
    repositories: List[Dict[str, str]] = Field(default_factory=list, env="REPOSITORIES")
    enable_comparative_analysis: bool = Field(default=True, env="ENABLE_COMPARATIVE_ANALYSIS")
    
    # Analysis Configuration
    analysis_year: int = Field(default=2025, env="ANALYSIS_YEAR")
    analysis_start_date: str = Field(default="2025-01-01", env="ANALYSIS_START_DATE")
    analysis_end_date: str = Field(default="2025-12-31", env="ANALYSIS_END_DATE")
    
    # Output Configuration
    output_dir: str = Field(default="./reports", env="OUTPUT_DIR")
    data_dir: str = Field(default="./data", env="DATA_DIR")
    dashboard_static_dir: str = Field(default="./dashboard/static/reports", env="DASHBOARD_STATIC_DIR")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Agent Configuration
    agent_name: str = Field(default="github_pr_analyzer", env="AGENT_NAME")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_analysis_date_range(self) -> tuple[datetime, datetime]:
        """Get the analysis date range as datetime objects."""
        start_date = datetime.strptime(self.analysis_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.analysis_end_date, "%Y-%m-%d")
        return start_date, end_date
    
    def ensure_directories(self) -> None:
        """Ensure output and data directories exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.dashboard_static_dir, exist_ok=True)


# Global settings instance
settings = Settings() 