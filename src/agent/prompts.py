"""
LangChain prompts for the GitHub PR Analytics AI Agent.
"""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage


# System message for the AI agent
SYSTEM_MESSAGE = """You are an expert data analyst specializing in GitHub repository analytics. 
Your task is to analyze pull request data and provide insightful observations about development patterns, 
team productivity, and code quality trends.

Key responsibilities:
1. Analyze monthly PR creation patterns
2. Identify trends and anomalies in the data
3. Provide actionable insights for development teams
4. Generate comprehensive reports with clear visualizations
5. Suggest improvements based on the data

Always provide data-driven insights and be specific about the numbers and trends you observe."""


# Prompt for analyzing monthly PR statistics
MONTHLY_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["monthly_stats", "year"],
    template="""Analyze the following monthly pull request statistics for {year}:

{monthly_stats}

Please provide:
1. A summary of the monthly PR creation patterns
2. Identification of peak activity months and potential reasons
3. Analysis of any seasonal trends or patterns
4. Comparison of merged vs closed PRs by month
5. Insights about team productivity and development velocity

Focus on actionable insights that could help improve the development process."""
)


# Prompt for overall repository analysis
OVERALL_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["overall_stats", "contributor_stats", "year"],
    template="""Analyze the overall pull request statistics for {year}:

Overall Statistics:
{overall_stats}

Contributor Statistics:
{contributor_stats}

Please provide:
1. Summary of repository health and activity level
2. Analysis of contributor engagement and distribution
3. Assessment of code review quality and collaboration
4. Identification of potential bottlenecks or areas for improvement
5. Recommendations for optimizing the PR workflow

Focus on metrics that indicate code quality, team collaboration, and development efficiency."""
)


# Prompt for trend analysis
TREND_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["trends", "monthly_stats", "year"],
    template="""Analyze the trends in pull request activity for {year}:

Trend Data:
{trends}

Monthly Statistics:
{monthly_stats}

Please provide:
1. Analysis of the overall trend direction (increasing, decreasing, stable)
2. Identification of significant changes or inflection points
3. Correlation with potential external factors (releases, team changes, etc.)
4. Predictions for future months based on current patterns
5. Recommendations for maintaining or improving the trend

Focus on understanding what drives the trends and how to optimize them."""
)


# Prompt for lifecycle analysis
LIFECYCLE_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["lifecycle_stats", "year"],
    template="""Analyze the pull request lifecycle statistics for {year}:

Lifecycle Statistics:
{lifecycle_stats}

Please provide:
1. Analysis of PR processing efficiency (time to close/merge)
2. Identification of bottlenecks in the review process
3. Assessment of code review quality and thoroughness
4. Comparison of merge rates and reasons for closure
5. Recommendations for optimizing the PR lifecycle

Focus on improving development velocity and code quality through better PR processes."""
)


# Prompt for generating executive summary
EXECUTIVE_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["summary", "key_insights", "year"],
    template="""Generate an executive summary for the GitHub PR analysis for {year}:

Summary Statistics:
{summary}

Key Insights:
{key_insights}

Please provide:
1. A concise executive summary highlighting the most important findings
2. Key performance indicators and their implications
3. Notable trends and their business impact
4. Recommendations for leadership consideration
5. Areas requiring attention or improvement

Keep the summary professional, data-driven, and actionable for decision-makers."""
)


# Prompt for generating detailed report
DETAILED_REPORT_PROMPT = PromptTemplate(
    input_variables=["analysis_data", "year"],
    template="""Generate a comprehensive detailed report for the GitHub PR analysis for {year}:

Analysis Data:
{analysis_data}

Please provide a detailed report including:
1. Executive Summary
2. Methodology and Data Overview
3. Monthly Analysis and Trends
4. Contributor Analysis
5. Lifecycle and Process Analysis
6. Key Findings and Insights
7. Recommendations and Action Items
8. Appendices with detailed statistics

Structure the report professionally with clear sections, data visualizations, and actionable recommendations."""
)


# Function to create system and human messages for chat
def create_analysis_messages(analysis_data: dict, prompt_type: str = "monthly") -> list:
    """Create system and human messages for LangChain chat."""
    messages = [
        SystemMessage(content=SYSTEM_MESSAGE)
    ]
    
    if prompt_type == "monthly":
        content = MONTHLY_ANALYSIS_PROMPT.format(
            monthly_stats=str(analysis_data.get("monthly_stats", {})),
            year=analysis_data.get("summary", {}).get("analysis_period", "2025")
        )
    elif prompt_type == "overall":
        content = OVERALL_ANALYSIS_PROMPT.format(
            overall_stats=str(analysis_data.get("overall_stats", {})),
            contributor_stats=str(analysis_data.get("contributor_stats", {})),
            year=analysis_data.get("summary", {}).get("analysis_period", "2025")
        )
    elif prompt_type == "trends":
        content = TREND_ANALYSIS_PROMPT.format(
            trends=str(analysis_data.get("trends", {})),
            monthly_stats=str(analysis_data.get("monthly_stats", {})),
            year=analysis_data.get("summary", {}).get("analysis_period", "2025")
        )
    elif prompt_type == "lifecycle":
        content = LIFECYCLE_ANALYSIS_PROMPT.format(
            lifecycle_stats=str(analysis_data.get("lifecycle_stats", {})),
            year=analysis_data.get("summary", {}).get("analysis_period", "2025")
        )
    elif prompt_type == "executive":
        content = EXECUTIVE_SUMMARY_PROMPT.format(
            summary=str(analysis_data.get("summary", {})),
            key_insights="[To be generated]",
            year=analysis_data.get("summary", {}).get("analysis_period", "2025")
        )
    elif prompt_type == "detailed":
        content = DETAILED_REPORT_PROMPT.format(
            analysis_data=str(analysis_data),
            year=analysis_data.get("summary", {}).get("analysis_period", "2025")
        )
    else:
        content = f"Please analyze the following GitHub PR data for 2025:\n\n{str(analysis_data)}"
    
    messages.append(HumanMessage(content=content))
    return messages 