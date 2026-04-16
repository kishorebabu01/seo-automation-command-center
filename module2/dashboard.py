# ============================================================
# SEO ANALYTICS DASHBOARD
# ============================================================
# A beautiful web dashboard showing:
# - How many pages generated
# - Which pages rank best
# - Click and impression data
# - Charts and graphs

from flask import Flask, render_template_string, jsonify
import json
import os
import pandas as pd
from gsc_tracker import get_sample_data, analyze_rankings

app = Flask(__name__)

# Load our generated pages data
def get_pages_data():
    output_dir = "output"
    pages = []
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith('.html') and f != 'index.html':
                # Parse filename to get service and city
                # "web-design-chennai.html" → service="Web Design", city="Chennai"
                name = f.replace('.html', '')
                parts = name.split('-')
                pages.append({
                    "filename": f,
                    "slug": name,
                    "url": f"http://localhost:5000/{f}"
                })
    return pages

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Command Center - Module 2 Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; }
        
        .header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header h1 { font-size: 1.5em; }
        .header .badge { background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.85em; }
        
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 30px 40px;
            background: #111;
        }
        
        .stat-card {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #333;
            text-align: center;
        }
        
        .stat-card .number { font-size: 2.5em; font-weight: 700; color: #667eea; }
        .stat-card .label { color: #888; margin-top: 5px; }
        .stat-card .change { color: #00ff88; font-size: 0.85em; margin-top: 8px; }
        
        .main-content { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; padding: 20px 40px; }
        
        .card {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #333;
        }
        
        .card h3 { margin-bottom: 20px; color: #667eea; font-size: 1.1em; }
        
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 10px; color: #888; font-size: 0.85em; border-bottom: 1px solid #333; }
        td { padding: 12px 10px; border-bottom: 1px solid #222; font-size: 0.9em; }
        tr:hover td { background: #16213e; }
        
        .position-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 700;
        }
        
        .pos-top3 { background: #00ff88; color: #000; }
        .pos-top10 { background: #667eea; color: #fff; }
        .pos-top20 { background: #ffaa00; color: #000; }
        .pos-below { background: #ff4444; color: #fff; }
        
        .chart-container { position: relative; height: 250px; }
        
        .pages-list { max-height: 300px; overflow-y: auto; }
        .page-item { padding: 10px; border-bottom: 1px solid #222; }
        .page-item a { color: #667eea; text-decoration: none; font-size: 0.9em; }
        .page-item a:hover { text-decoration: underline; }
        
        .full-width { grid-column: 1 / -1; }
    </style>
</head>
<body>

<div class="header">
    <div>
        <h1>🚀 SEO Automation Command Center</h1>
        <div style="color:rgba(255,255,255,0.7); font-size:0.9em; margin-top:5px;">Module 2: Programmatic SEO Engine</div>
    </div>
    <div class="badge">📊 Live Dashboard</div>
</div>

<div class="stats-row">
    <div class="stat-card">
        <div class="number" id="total-pages">-</div>
        <div class="label">Pages Generated</div>
        <div class="change">✅ Auto-generated</div>
    </div>
    <div class="stat-card">
        <div class="number" id="total-clicks">-</div>
        <div class="label">Total Clicks</div>
        <div class="change">📈 Last 30 days</div>
    </div>
    <div class="stat-card">
        <div class="number" id="total-impressions">-</div>
        <div class="label">Impressions</div>
        <div class="change">👁️ Times shown in Google</div>
    </div>
    <div class="stat-card">
        <div class="number" id="avg-position">-</div>
        <div class="label">Avg. Position</div>
        <div class="change">🎯 Google ranking</div>
    </div>
</div>

<div class="main-content">
    
    <!-- Rankings Table -->
    <div class="card">
        <h3>🏆 Keyword Rankings</h3>
        <table>
            <thead>
                <tr>
                    <th>Keyword</th>
                    <th>Position</th>
                    <th>Clicks</th>
                    <th>Impressions</th>
                    <th>CTR</th>
                </tr>
            </thead>
            <tbody id="rankings-table">
                <tr><td colspan="5" style="text-align:center; color:#888;">Loading...</td></tr>
            </tbody>
        </table>
    </div>
    
    <!-- Charts -->
    <div style="display:flex; flex-direction:column; gap:20px;">
        <div class="card">
            <h3>📊 Ranking Distribution</h3>
            <div class="chart-container">
                <canvas id="rankChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h3>📄 Generated Pages</h3>
            <div class="pages-list" id="pages-list">
                Loading...
            </div>
        </div>
    </div>
    
    <!-- Clicks Chart - Full Width -->
    <div class="card full-width">
        <h3>📈 Clicks by Page (Top 8)</h3>
        <div class="chart-container" style="height:200px;">
            <canvas id="clicksChart"></canvas>
        </div>
    </div>

</div>

<script>
// Load data from API
async function loadDashboard() {
    const res = await fetch('/api/data');
    const data = await res.json();
    
    // Update stat cards
    document.getElementById('total-pages').textContent = data.total_pages;
    document.getElementById('total-clicks').textContent = data.analysis.total_clicks.toLocaleString();
    document.getElementById('total-impressions').textContent = data.analysis.total_impressions.toLocaleString();
    document.getElementById('avg-position').textContent = data.analysis.avg_position;
    
    // Update rankings table
    const tbody = document.getElementById('rankings-table');
    tbody.innerHTML = '';
    data.rankings.forEach(r => {
        let posClass = r.position <= 3 ? 'pos-top3' : r.position <= 10 ? 'pos-top10' : r.position <= 20 ? 'pos-top20' : 'pos-below';
        tbody.innerHTML += `
            <tr>
                <td>${r.query}</td>
                <td><span class="position-badge ${posClass}">#${r.position}</span></td>
                <td>${r.clicks}</td>
                <td>${r.impressions.toLocaleString()}</td>
                <td>${r.ctr}%</td>
            </tr>
        `;
    });
    
    // Update pages list
    const pagesList = document.getElementById('pages-list');
    pagesList.innerHTML = data.pages.slice(0, 20).map(p => 
        `<div class="page-item"><a href="http://localhost:5000/${p.filename}" target="_blank">📄 ${p.filename}</a></div>`
    ).join('');
    
    // Ranking Distribution Pie Chart
    const rankCtx = document.getElementById('rankChart').getContext('2d');
    new Chart(rankCtx, {
        type: 'doughnut',
        data: {
            labels: ['Top 3 🏆', 'Top 10 ✅', 'Top 20 📈', 'Below 20 ⚠️'],
            datasets: [{
                data: [
                    data.analysis.top_3.length,
                    data.analysis.top_10.length,
                    data.analysis.top_20.length,
                    data.analysis.below_20.length
                ],
                backgroundColor: ['#00ff88', '#667eea', '#ffaa00', '#ff4444'],
                borderWidth: 0
            }]
        },
        options: { responsive: true, maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#fff', font: { size: 11 } } } }
        }
    });
    
    // Clicks Bar Chart
    const clicksCtx = document.getElementById('clicksChart').getContext('2d');
    const top8 = data.rankings.slice(0, 8);
    new Chart(clicksCtx, {
        type: 'bar',
        data: {
            labels: top8.map(r => r.query.substring(0, 20)),
            datasets: [{
                label: 'Clicks',
                data: top8.map(r => r.clicks),
                backgroundColor: '#667eea',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#888' }, grid: { color: '#222' } },
                y: { ticks: { color: '#888' }, grid: { color: '#222' } }
            }
        }
    });
}

loadDashboard();
</script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/data')
def api_data():
    """API endpoint that returns all dashboard data as JSON"""
    rankings = get_sample_data()
    analysis = analyze_rankings(rankings)
    pages = get_pages_data()
    
    return jsonify({
        "total_pages": len(pages),
        "rankings": rankings,
        "analysis": {
            "total_clicks": analysis["total_clicks"],
            "total_impressions": analysis["total_impressions"],
            "avg_position": analysis["avg_position"],
            "top_3": analysis["top_3"],
            "top_10": analysis["top_10"],
            "top_20": analysis["top_20"],
            "below_20": analysis["below_20"]
        },
        "pages": pages
    })

if __name__ == '__main__':
    print("📊 Starting SEO Dashboard...")
    print("🔗 Open: http://localhost:5001")
    app.run(debug=True, port=5001)