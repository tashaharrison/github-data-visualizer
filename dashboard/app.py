#!/usr/bin/env python3
"""
Flask dashboard for GitHub PR Analytics.
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import plotly.graph_objs as go
import plotly.utils
from loguru import logger

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings


app = Flask(__name__)
CORS(app)

# Configure logging
logger.add("logs/dashboard.log", rotation="1 day", retention="30 days")


class DashboardData:
    """Manages dashboard data and reports."""
    
    def __init__(self):
        self.reports_dir = Path(settings.output_dir)
        self.data_dir = Path(settings.data_dir)
        self.analysis_year = settings.analysis_year
    
    def get_available_reports(self):
        """Get list of available reports."""
        reports = []
        
        # Look for analysis files
        analysis_files = glob.glob(str(self.reports_dir / "*_analysis_*.json"))
        
        for file_path in analysis_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extract report info
                filename = Path(file_path).name
                if "multi_repo" in filename:
                    report_type = "Multi-Repository Analysis"
                    repo_count = data.get("summary", {}).get("total_repositories", 0)
                    total_prs = data.get("summary", {}).get("total_prs_across_repos", 0)
                    title = f"Multi-Repository Analysis ({repo_count} repos, {total_prs} PRs)"
                else:
                    report_type = "Single Repository Analysis"
                    total_prs = data.get("summary", {}).get("total_prs", 0)
                    
                    # Extract repository name from filename and map to display name
                    repo_name = filename.replace("_analysis_2025.json", "")
                    display_name = self._get_repository_display_name(repo_name)
                    title = f"{display_name} Analysis ({total_prs} PRs)"
                
                reports.append({
                    "filename": filename,
                    "filepath": file_path,
                    "type": report_type,
                    "title": title,
                    "generated_at": data.get("summary", {}).get("generated_at", ""),
                    "data": data
                })
            except Exception as e:
                logger.error(f"Error reading report {file_path}: {e}")
        
        return sorted(reports, key=lambda x: x["generated_at"], reverse=True)
    
    def get_visualizations(self):
        """Get list of available visualizations."""
        viz_files = []
        
        # Look for image files in dashboard static directory only
        image_extensions = ["*.png", "*.jpg", "*.jpeg"]
        dashboard_static_dir = Path(settings.dashboard_static_dir)
        
        for ext in image_extensions:
            viz_files.extend(glob.glob(str(dashboard_static_dir / ext)))
        
        visualizations = []
        for file_path in viz_files:
            filename = Path(file_path).name
            created_time = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
            
            # Categorize visualizations
            if "monthly" in filename:
                category = "Monthly Trends"
            elif "state_distribution" in filename:
                category = "PR States"
            elif "contributor" in filename:
                category = "Contributors"
            elif "lifecycle" in filename:
                category = "Lifecycle"
            elif "comparison" in filename:
                category = "Comparisons"
            elif "heatmap" in filename:
                category = "Activity Heatmaps"
            elif "radar" in filename:
                category = "Quality Metrics"
            else:
                category = "Other"
            
            visualizations.append({
                "filename": filename,
                "filepath": file_path,
                "category": category,
                "created_at": created_time.isoformat(),
                "url": f"/static/reports/{filename}"
            })
        
        return sorted(visualizations, key=lambda x: x["created_at"], reverse=True)
    
    def get_insights_files(self):
        """Get list of insight files."""
        insight_files = []
        
        # Look for insight files
        insight_patterns = ["*_insights_*.txt", "*_insights_*.json"]
        for pattern in insight_patterns:
            insight_files.extend(glob.glob(str(self.reports_dir / pattern)))
        
        insights = []
        for file_path in insight_files:
            filename = Path(file_path).name
            created_time = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
            
            # Categorize insights
            if "monthly" in filename:
                category = "Monthly Insights"
            elif "overall" in filename:
                category = "Overall Analysis"
            elif "comparative" in filename:
                category = "Comparative Insights"
            else:
                category = "General Insights"
            
            insights.append({
                "filename": filename,
                "filepath": file_path,
                "category": category,
                "created_at": created_time.isoformat()
            })
        
        return sorted(insights, key=lambda x: x["created_at"], reverse=True)
    def _get_repository_display_name(self, repo_name):
        """
        Get the display name for a repository from the settings (from .env or config).
        Falls back to the repo_name if no display_name is configured.
        """
        from config.settings import settings

        # Try to get repositories config from settings
        repo_configs = getattr(settings, "repositories", None)
        if repo_configs:
            import json
            try:
                if isinstance(repo_configs, str):
                    repo_configs = json.loads(repo_configs)
                for repo in repo_configs:
                    # Support both dict and object
                    if isinstance(repo, dict):
                        if repo.get("name") == repo_name:
                            return repo.get("display_name", repo_name)
            except Exception:
                pass  # Fallback below

        # Fallback: replace underscores with spaces to match .env format
        return repo_name.replace("_", " ")


# Initialize dashboard data
dashboard_data = DashboardData()


@app.route('/')
def index():
    """Main dashboard page."""
    reports = dashboard_data.get_available_reports()
    visualizations = dashboard_data.get_visualizations()
    insights = dashboard_data.get_insights_files()
    
    return render_template('index.html', 
                         reports=reports,
                         visualizations=visualizations,
                         insights=insights,
                         analysis_year=settings.analysis_year)


@app.route('/api/reports')
def api_reports():
    """API endpoint for reports."""
    reports = dashboard_data.get_available_reports()
    return jsonify(reports)


@app.route('/api/visualizations')
def api_visualizations():
    """API endpoint for visualizations."""
    visualizations = dashboard_data.get_visualizations()
    return jsonify(visualizations)


@app.route('/api/insights')
def api_insights():
    """API endpoint for insights."""
    insights = dashboard_data.get_insights_files()
    return jsonify(insights)


@app.route('/report/<filename>')
def view_report(filename):
    """View a specific report."""
    reports = dashboard_data.get_available_reports()
    report = next((r for r in reports if r["filename"] == filename), None)
    
    if not report:
        return "Report not found", 404
    
    return render_template('report.html', report=report)


@app.route('/api/report/<filename>')
def api_report(filename):
    """API endpoint for specific report data."""
    reports = dashboard_data.get_available_reports()
    report = next((r for r in reports if r["filename"] == filename), None)
    
    if not report:
        return jsonify({"error": "Report not found"}), 404
    
    return jsonify(report["data"])


@app.route('/reports/<filename>')
def serve_report_file(filename):
    """Serve report files."""
    # First try dashboard static directory, then fall back to reports directory
    dashboard_static_path = Path(settings.dashboard_static_dir)
    reports_path = Path(settings.output_dir)
    
    logger.info(f"Serving file: {filename}")
    logger.info(f"Dashboard static path: {dashboard_static_path}")
    logger.info(f"Reports path: {reports_path}")
    
    # Check if file exists in dashboard static directory
    dashboard_file = dashboard_static_path / filename
    reports_file = reports_path / filename
    
    logger.info(f"Dashboard file exists: {dashboard_file.exists()}")
    logger.info(f"Reports file exists: {reports_file.exists()}")
    
    if dashboard_file.exists():
        logger.info(f"Serving from dashboard static: {dashboard_file}")
        return send_from_directory(settings.dashboard_static_dir, filename)
    elif reports_file.exists():
        logger.info(f"Serving from reports: {reports_file}")
        return send_from_directory(settings.output_dir, filename)
    else:
        logger.error(f"File not found: {filename}")
        return "File not found", 404


@app.route('/insight/<filename>')
def view_insight(filename):
    """View a specific insight file."""
    insights = dashboard_data.get_insights_files()
    insight = next((i for i in insights if i["filename"] == filename), None)
    
    if not insight:
        return "Insight file not found", 404
    
    try:
        with open(insight["filepath"], 'r') as f:
            content = f.read()
    except Exception as e:
        content = f"Error reading file: {e}"
    
    return render_template('insight.html', insight=insight, content=content)


@app.route('/api/charts/<filename>')
def api_charts(filename):
    """Generate interactive charts for a report."""
    logger.info(f"Generating charts for: {filename}")
    
    reports = dashboard_data.get_available_reports()
    report = next((r for r in reports if r["filename"] == filename), None)
    
    if not report:
        logger.error(f"Report not found: {filename}")
        return jsonify({"error": "Report not found"}), 404
    
    data = report["data"]
    logger.info(f"Report data keys: {list(data.keys())}")
    
    charts = {}
    
    try:
        # Generate monthly PR chart
        if "monthly_stats" in data and data["monthly_stats"]:
            monthly_stats = data["monthly_stats"]
            months = list(monthly_stats.keys())
            counts = [stats["count"] for stats in monthly_stats.values()]
            
            fig = go.Figure(data=[
                go.Bar(x=months, y=counts, name="PR Count", marker_color='#0366d6')
            ])
            fig.update_layout(
                title="Monthly Pull Requests",
                xaxis_title="Month",
                yaxis_title="Number of PRs",
                template="plotly_white",
                height=400
            )
            charts["monthly_prs"] = json.loads(fig.to_json())
        
        # Generate merge rate gauge chart
        if "overall_stats" in data and data["overall_stats"]:
            overall_stats = data["overall_stats"]
            if "merge_rate" in overall_stats:
                fig = go.Figure(data=[
                    go.Indicator(
                        mode="gauge+number",
                        value=overall_stats["merge_rate"],
                        title={'text': "Merge Rate (%)"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#0366d6"},
                            'steps': [
                                {'range': [0, 50], 'color': "#ff6b6b"},
                                {'range': [50, 80], 'color': "#ffd93d"},
                                {'range': [80, 100], 'color': "#6bcf7f"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    )
                ])
                fig.update_layout(
                    template="plotly_white",
                    height=400
                )
                charts["merge_rate"] = json.loads(fig.to_json())
        
        # Generate contributor chart
        if "contributor_stats" in data and data["contributor_stats"]:
            contributor_stats = data["contributor_stats"]
            if "top_contributors" in contributor_stats and contributor_stats["top_contributors"]:
                contributors = contributor_stats["top_contributors"][:10]  # Top 10
                names = [contrib[0] for contrib in contributors]
                pr_counts = [contrib[1]["pr_count"] for contrib in contributors]
                
                fig = go.Figure(data=[
                    go.Bar(x=pr_counts, y=names, orientation='h', marker_color='#28a745')
                ])
                fig.update_layout(
                    title="Top Contributors by PR Count",
                    xaxis_title="Number of PRs",
                    yaxis_title="Contributor",
                    template="plotly_white",
                    height=400
                )
                charts["top_contributors"] = json.loads(fig.to_json())
        
        # Generate lifecycle chart
        if "lifecycle_stats" in data and data["lifecycle_stats"]:
            lifecycle_stats = data["lifecycle_stats"]
            if "avg_time_to_merge" in lifecycle_stats:
                fig = go.Figure(data=[
                    go.Indicator(
                        mode="number+delta",
                        value=lifecycle_stats["avg_time_to_merge"],
                        title={'text': "Avg Time to Merge (hours)"},
                        delta={'reference': 24, 'relative': True},
                        number={'suffix': "h"}
                    )
                ])
                fig.update_layout(
                    template="plotly_white",
                    height=300
                )
                charts["avg_time_to_merge"] = json.loads(fig.to_json())
        
        # Generate state distribution pie chart
        if "overall_stats" in data and data["overall_stats"]:
            overall_stats = data["overall_stats"]
            if "state_distribution" in overall_stats and overall_stats["state_distribution"]:
                states = list(overall_stats["state_distribution"].keys())
                counts = list(overall_stats["state_distribution"].values())
                
                fig = go.Figure(data=[
                    go.Pie(labels=states, values=counts, hole=0.3)
                ])
                fig.update_layout(
                    title="PR State Distribution",
                    template="plotly_white",
                    height=400
                )
                charts["state_distribution"] = json.loads(fig.to_json())
        
        logger.info(f"Generated {len(charts)} charts for {filename}")
        
    except Exception as e:
        logger.error(f"Error generating charts for {filename}: {e}")
        charts = {"error": f"Error generating charts: {str(e)}"}
    
    return jsonify(charts)


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "reports_count": len(dashboard_data.get_available_reports()),
        "visualizations_count": len(dashboard_data.get_visualizations())
    })


@app.route('/api/test-chart')
def test_chart():
    """Test chart generation with sample data."""
    try:
        import plotly.graph_objs as go
        
        # Create a simple test chart
        fig = go.Figure(data=[
            go.Bar(x=['Jan', 'Feb', 'Mar'], y=[10, 20, 15], name="Test Data")
        ])
        fig.update_layout(
            title="Test Chart",
            xaxis_title="Month",
            yaxis_title="Value",
            template="plotly_white"
        )
        
        chart_data = json.loads(fig.to_json())
        logger.info("Test chart generated successfully")
        return jsonify({"test_chart": chart_data})
        
    except Exception as e:
        logger.error(f"Error generating test chart: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/test')
def test_page():
    """Test page for debugging charts."""
    return render_template('test.html')


@app.route('/test-file/<filename>')
def test_file(filename):
    """Test file serving."""
    dashboard_static_path = Path(settings.dashboard_static_dir)
    reports_path = Path(settings.output_dir)
    
    logger.info(f"Testing file: {filename}")
    logger.info(f"Dashboard static path: {dashboard_static_path}")
    logger.info(f"Reports path: {reports_path}")
    
    dashboard_file = dashboard_static_path / filename
    reports_file = reports_path / filename
    
    logger.info(f"Dashboard file exists: {dashboard_file.exists()}")
    logger.info(f"Reports file exists: {reports_file.exists()}")
    
    if dashboard_file.exists():
        return f"File exists in dashboard static: {dashboard_file}"
    elif reports_file.exists():
        return f"File exists in reports: {reports_file}"
    else:
        return f"File not found: {filename}"


if __name__ == '__main__':
    # Ensure directories exist
    settings.ensure_directories()
    Path("logs").mkdir(exist_ok=True)
    
    print("🚀 Starting GitHub PR Analytics Dashboard")
    print(f"📊 Reports directory: {settings.output_dir}")
    print(f"🔧 Analysis year: {settings.analysis_year}")
    print("🌐 Dashboard available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 