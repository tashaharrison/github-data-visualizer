# GitHub PR Analytics AI Agent

An AI agent that uses LangChain, OpenAI, and the GitHub MCP server to analyze pull request creation patterns for 2025.

## Overview

This agent connects to GitHub via the Model Context Protocol (MCP) server to fetch pull request data and uses OpenAI's language model through LangChain to analyze and report on PR creation trends.

## Features

- Connects to GitHub using MCP server
- Fetches pull request data for 2025
- Analyzes monthly PR creation patterns
- **Multi-repository analysis and comparison**
- **Comparative insights across repositories**
- Generates insights using OpenAI
- Provides detailed reports and visualizations

## Project Structure

```
github-connector/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── config/
│   └── settings.py          # Configuration settings
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── github_agent.py  # Main agent implementation
│   │   └── prompts.py       # LangChain prompts
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── github_client.py # GitHub MCP client
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── pr_analyzer.py   # PR data analysis
│   │   └── visualizer.py    # Data visualization
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── data/
│   └── .gitkeep             # Data storage directory
├── reports/
│   └── .gitkeep             # Generated reports directory
├── main.py                  # Entry point
├── cleanup_reports.py       # Standalone cleanup script
└── configure_repos.py       # Repository configuration script
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Configure Repositories**
   
   **For Single Repository:**
   ```bash
   # Edit .env file
   REPO_OWNER=your_organization
   REPO_NAME=your_repository
   ```
   
   **For Multiple Repositories:**
   ```bash
   # Option 1: Use the interactive configuration script
   python configure_repos.py
   
   # Option 2: Edit .env file manually
   REPOSITORIES=[{"owner": "your_org", "name": "repo1"}, {"owner": "your_org", "name": "repo2"}]
   ```

4. **Run the Agent**
   ```bash
   # Run analysis (will automatically clean up existing reports)
   python main.py
   
   # Run analysis with explicit cleanup
   python main.py --cleanup
   
   # Clean up existing reports only
   python main.py --cleanup-only
   
   # Or use the standalone cleanup script
   python cleanup_reports.py
   ```

5. **Start the Dashboard**
   ```bash
   python dashboard/app.py
   ```
   Then open http://localhost:5000 in your browser

## Configuration

The agent requires the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GITHUB_TOKEN`: GitHub personal access token
- `MCP_SERVER_URL`: GitHub MCP server URL
- `REPO_OWNER`: Repository owner/organization (for single repo analysis)
- `REPO_NAME`: Repository name to analyze (for single repo analysis)
- `REPOSITORIES`: JSON array of repositories for multi-repo analysis (optional)
- `ENABLE_COMPARATIVE_ANALYSIS`: Enable comparative analysis across repositories (default: true)

## Output

The agent generates:
- Monthly PR creation statistics
- Trend analysis and insights
- **Comparative analysis across repositories**
- **Repository rankings and quality metrics**
- Visual charts and graphs
- Detailed reports in JSON and CSV formats

## Report Management

The agent automatically manages reports to prevent clutter:
- **Automatic Cleanup**: Existing reports are automatically deleted before generating new ones
- **Manual Cleanup**: Use `python main.py --cleanup-only` or `python cleanup_reports.py` to clean up manually
- **Selective Cleanup**: Use `python main.py --cleanup` to explicitly clean up before running analysis

### Multi-Repository Analysis

When analyzing multiple repositories, the agent provides:
- Individual repository analysis
- Comparative statistics and rankings
- Cross-repository insights
- Quality metrics comparison
- Activity heatmaps across repositories

### Web Dashboard

The dashboard provides:
- **Interactive Overview**: Real-time statistics and summaries
- **Report Browser**: View and explore detailed analysis reports
- **Visualization Gallery**: Browse charts and graphs with full-size viewing
- **AI Insights Reader**: Read and export AI-generated insights
- **Interactive Charts**: Dynamic charts powered by Plotly.js
- **Search & Filter**: Find specific reports or visualizations quickly
- **Export Functionality**: Download reports and insights in various formats

## Dependencies

- LangChain: AI framework
- OpenAI: Language model provider
- GitHub MCP: GitHub data access
- Pandas: Data manipulation
- Matplotlib: Data visualization
- Pydantic: Data validation 