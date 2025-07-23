#!/usr/bin/env python3
"""
CKAN Interactive Dashboard - Live Feature Demo
Demonstrates real-time CKAN integration with modern UI patterns
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import html

class CKANDashboard:
    """Interactive CKAN dashboard with live data integration"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/3"
        
    def get_live_metrics(self) -> Dict:
        """Get real-time portal metrics with error handling"""
        try:
            # Test connection first
            health_check = requests.get(f"{self.base_url}/api/3/action/status_show", timeout=5)
            
            if health_check.status_code == 200:
                # Get dataset statistics
                pkg_response = requests.get(f"{self.api_url}/action/package_search", 
                                          params={"rows": 0}, timeout=5)
                pkg_data = pkg_response.json()
                
                # Get organization data  
                org_response = requests.get(f"{self.api_url}/action/organization_list", timeout=5)
                org_data = org_response.json()
                
                return {
                    "status": "✅ ONLINE",
                    "datasets": pkg_data["result"]["count"],
                    "organizations": len(org_data["result"]),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "api_version": "3.0",
                    "connection": "Active"
                }
            else:
                raise Exception("API not responding")
                
        except Exception as e:
            return {
                "status": "⚠️ OFFLINE",
                "datasets": "N/A",
                "organizations": "N/A", 
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "api_version": "N/A",
                "connection": f"Error: {str(e)}"
            }
    
    def generate_sample_data_catalog(self) -> List[Dict]:
        """Generate sample government datasets showcasing CKAN's data model"""
        datasets = [
            {
                "title": "City Budget FY2025",
                "description": "Annual budget allocations by department",
                "format": "CSV/JSON",
                "last_updated": "2025-01-15",
                "downloads": 1247,
                "category": "Finance",
                "status": "Updated"
            },
            {
                "title": "Traffic Safety Reports", 
                "description": "Intersection accident data and analysis",
                "format": "JSON/GeoJSON",
                "last_updated": "2025-01-20",
                "downloads": 892,
                "category": "Transportation",
                "status": "New"
            },
            {
                "title": "Zoning District Maps",
                "description": "Current zoning classifications and boundaries", 
                "format": "Shapefile/KML",
                "last_updated": "2025-01-10",
                "downloads": 2156,
                "category": "Planning",
                "status": "Updated"
            },
            {
                "title": "Public Meeting Minutes",
                "description": "City council and committee meeting records",
                "format": "PDF/HTML", 
                "last_updated": "2025-01-22",
                "downloads": 445,
                "category": "Governance",
                "status": "New"
            }
        ]
        return datasets
    
    def create_html_dashboard(self) -> str:
        """Generate a complete HTML dashboard showcasing CKAN integration"""
        metrics = self.get_live_metrics()
        datasets = self.generate_sample_data_catalog()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CKAN Government Data Portal Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(0);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .datasets-section {{
            margin-top: 40px;
        }}
        
        .datasets-section h2 {{
            color: #2c3e50;
            font-size: 2em;
            margin-bottom: 25px;
            text-align: center;
        }}
        
        .dataset-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .dataset-card {{
            background: white;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }}
        
        .dataset-card:hover {{
            border-color: #667eea;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .dataset-title {{
            color: #2c3e50;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .dataset-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ecf0f1;
        }}
        
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .status-new {{
            background: #e8f5e8;
            color: #27ae60;
        }}
        
        .status-updated {{
            background: #e3f2fd;
            color: #2196f3;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}
        
        .timestamp {{
            background: #34495e;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ CKAN Government Data Portal</h1>
            <p>Live Dashboard - City of Demo Implementation</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{metrics['datasets']}</div>
                <div class="metric-label">Total Datasets</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['organizations']}</div>
                <div class="metric-label">Organizations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['status']}</div>
                <div class="metric-label">Portal Status</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">API v{metrics['api_version']}</div>
                <div class="metric-label">CKAN Version</div>
            </div>
        </div>
        
        <div class="datasets-section">
            <h2>📊 Featured Government Datasets</h2>
            <div class="dataset-grid">
"""
        
        # Add dataset cards
        for dataset in datasets:
            status_class = "status-new" if dataset['status'] == "New" else "status-updated"
            html_content += f"""
                <div class="dataset-card">
                    <div class="dataset-title">{html.escape(dataset['title'])}</div>
                    <p style="color: #7f8c8d; line-height: 1.5;">{html.escape(dataset['description'])}</p>
                    <div style="margin: 15px 0;">
                        <strong>Format:</strong> {html.escape(dataset['format'])}<br>
                        <strong>Category:</strong> {html.escape(dataset['category'])}<br>
                        <strong>Downloads:</strong> {dataset['downloads']:,}
                    </div>
                    <div class="dataset-meta">
                        <span>Updated: {dataset['last_updated']}</span>
                        <span class="status-badge {status_class}">{dataset['status']}</span>
                    </div>
                </div>
"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="footer">
            <h3>🎯 CKAN Modernization Project Achievement</h3>
            <p>Demonstrates: Real-time API integration • Modern UI/UX • Government data standards</p>
            <p><strong>Connection Status:</strong> {metrics['connection']}</p>
            <div class="timestamp">
                Last Updated: {metrics['last_updated']}
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def save_dashboard(self) -> str:
        """Save the dashboard and return the filename"""
        dashboard_html = self.create_html_dashboard()
        filename = f"ckan_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
            
        return filename

def main():
    """Generate the interactive CKAN dashboard"""
    print("🚀 Generating Interactive CKAN Dashboard...")
    print("=" * 50)
    
    dashboard = CKANDashboard()
    filename = dashboard.save_dashboard()
    
    print(f"✅ Dashboard created: {filename}")
    print("🌐 Open this file in your browser for the live demo!")
    print("📹 Perfect for video presentation - shows real CKAN integration!")
    print("\n🎯 This demonstrates:")
    print("  • Real-time CKAN API integration")
    print("  • Modern responsive web design")  
    print("  • Government data portal UX")
    print("  • Production-ready dashboard development")

if __name__ == "__main__":
    main() 