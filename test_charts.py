#!/usr/bin/env python3
"""
Test script to debug chart generation issues.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from config.settings import settings


def test_chart_generation():
    """Test chart generation with sample data."""
    print("🔧 Testing Chart Generation")
    print("=" * 40)
    
    # Check if reports directory exists
    reports_dir = Path(settings.output_dir)
    if not reports_dir.exists():
        print(f"❌ Reports directory not found: {reports_dir}")
        return
    
    # Look for analysis files
    analysis_files = list(reports_dir.glob("*_analysis_*.json"))
    
    if not analysis_files:
        print("❌ No analysis files found")
        print(f"📁 Checked directory: {reports_dir}")
        return
    
    print(f"✅ Found {len(analysis_files)} analysis files")
    
    # Test each file
    for file_path in analysis_files:
        print(f"\n📄 Testing: {file_path.name}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"  📊 Data structure:")
            print(f"    - Summary: {'✅' if 'summary' in data else '❌'}")
            print(f"    - Monthly stats: {'✅' if 'monthly_stats' in data else '❌'}")
            print(f"    - Overall stats: {'✅' if 'overall_stats' in data else '❌'}")
            print(f"    - Contributor stats: {'✅' if 'contributor_stats' in data else '❌'}")
            print(f"    - Lifecycle stats: {'✅' if 'lifecycle_stats' in data else '❌'}")
            
            # Test chart generation
            test_charts_for_data(data, file_path.name)
            
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    
    print("\n🎯 Chart Generation Test Complete")


def test_charts_for_data(data, filename):
    """Test chart generation for specific data."""
    try:
        import plotly.graph_objs as go
        
        charts = {}
        
        # Test monthly PR chart
        if "monthly_stats" in data and data["monthly_stats"]:
            monthly_stats = data["monthly_stats"]
            months = list(monthly_stats.keys())
            counts = [stats["count"] for stats in monthly_stats.values()]
            
            if months and counts:
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
                print(f"    ✅ Monthly PR chart: {len(months)} months, {sum(counts)} total PRs")
            else:
                print(f"    ❌ Monthly PR chart: No data")
        
        # Test merge rate chart
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
                            ]
                        }
                    )
                ])
                fig.update_layout(template="plotly_white", height=400)
                charts["merge_rate"] = json.loads(fig.to_json())
                print(f"    ✅ Merge rate chart: {overall_stats['merge_rate']:.2f}%")
            else:
                print(f"    ❌ Merge rate chart: No merge_rate data")
        
        # Test contributor chart
        if "contributor_stats" in data and data["contributor_stats"]:
            contributor_stats = data["contributor_stats"]
            if "top_contributors" in contributor_stats and contributor_stats["top_contributors"]:
                contributors = contributor_stats["top_contributors"][:10]
                names = [contrib[0] for contrib in contributors]
                pr_counts = [contrib[1]["pr_count"] for contrib in contributors]
                
                if names and pr_counts:
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
                    print(f"    ✅ Contributor chart: {len(contributors)} contributors")
                else:
                    print(f"    ❌ Contributor chart: No contributor data")
            else:
                print(f"    ❌ Contributor chart: No top_contributors data")
        
        print(f"    📈 Generated {len(charts)} charts successfully")
        
        # Save test charts
        test_charts_file = Path(settings.output_dir) / f"test_charts_{filename}"
        with open(test_charts_file, 'w') as f:
            json.dump(charts, f, indent=2)
        print(f"    💾 Test charts saved to: {test_charts_file}")
        
    except Exception as e:
        print(f"    ❌ Error generating charts: {e}")


def test_dashboard_api():
    """Test dashboard API endpoints."""
    print("\n🌐 Testing Dashboard API")
    print("=" * 40)
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # Test reports endpoint
        try:
            response = requests.get(f"{base_url}/api/reports", timeout=5)
            if response.status_code == 200:
                reports = response.json()
                print(f"✅ Reports API: {len(reports)} reports found")
            else:
                print(f"❌ Reports API: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Reports API: {e}")
        
        # Test visualizations endpoint
        try:
            response = requests.get(f"{base_url}/api/visualizations", timeout=5)
            if response.status_code == 200:
                viz = response.json()
                print(f"✅ Visualizations API: {len(viz)} visualizations found")
            else:
                print(f"❌ Visualizations API: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Visualizations API: {e}")
        
    except ImportError:
        print("❌ Requests library not available for API testing")


if __name__ == "__main__":
    print("🚀 GitHub PR Analytics - Chart Debug Tool")
    print("=" * 50)
    
    test_chart_generation()
    test_dashboard_api()
    
    print("\n📋 Summary:")
    print("- Check the console output above for any errors")
    print("- If charts are still not showing, check browser console for JavaScript errors")
    print("- Ensure Plotly.js is loaded correctly in the browser")
    print("- Verify that the dashboard is running on http://localhost:5000") 