#!/usr/bin/env python3
"""
build_static_dashboard.py
Generates a self-contained static index.html from output.json
that works on GitHub Pages without a backend server.
NOW INCLUDES: Client-side single stock search via Yahoo Finance API
"""

import json
import os
from datetime import datetime

OUTPUT_PATH = "output.json"
STATIC_INDEX_PATH = "_site/index.html"

def load_output():
    if not os.path.exists(OUTPUT_PATH):
        print(f"WARNING: {OUTPUT_PATH} not found. Creating empty dashboard.")
        return {
            "timestamp": datetime.now().isoformat(),
            "engine": "-",
            "kpi": {"universe": 0, "in_debate": 0, "buy_signals": 0, "top_pick": "-", "top_pick_confidence": 0},
            "verdicts": [],
            "total_verdicts": 0,
        }
    with open(OUTPUT_PATH, "r") as f:
        return json.load(f)

def generate_static_html(data):
    kpi = data.get("kpi", {})
    verdicts = data.get("verdicts", [])
    engine = data.get("engine", "-")
    timestamp = data.get("timestamp", "-")

    buy_count = sum(1 for v in verdicts if v.get("verdict") == "BUY")
    watch_count = sum(1 for v in verdicts if v.get("verdict") == "WATCH")
    avoid_count = sum(1 for v in verdicts if v.get("verdict") == "AVOID")

    verdict_rows = []
    for v in verdicts[:20]:
        symbol = v.get("symbol", "?")
        name = v.get("name", symbol)
        verdict = v.get("verdict", "WATCH")
        confidence = v.get("confidence", 0)
        winner = v.get("winner", "-")
        rationale = v.get("rationale", "")
        live_price = v.get("live_price", "-")
        day_change = v.get("day_change_pct", "-")

        badge_color = {"BUY": "#16a34a", "WATCH": "#ca8a04", "AVOID": "#dc2626"}.get(verdict, "#6b7280")
        change_color = "#16a34a"
        try:
            if day_change and float(str(day_change).replace("+","")) < 0:
                change_color = "#dc2626"
        except:
            pass
        rationale_short = rationale[:80] + "..." if len(rationale) > 80 else rationale

        verdict_rows.append(
            '<tr style="border-bottom:1px solid #e5e7eb">'
            f'<td style="padding:12px 16px;font-weight:600">{symbol}</td>'
            f'<td style="padding:12px 16px;color:#6b7280;font-size:13px">{name}</td>'
            f'<td style="padding:12px 16px"><span style="background:{badge_color};color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:600">{verdict}</span></td>'
            f'<td style="padding:12px 16px;text-align:center;font-weight:700">{confidence}/10</td>'
            f'<td style="padding:12px 16px;color:#6b7280;font-size:13px">{winner}</td>'
            f'<td style="padding:12px 16px;color:#6b7280;font-size:13px">&#8377;{live_price}</td>'
            f'<td style="padding:12px 16px;color:{change_color};font-weight:600">{day_change}%</td>'
            f'<td style="padding:12px 16px;color:#6b7280;font-size:12px;max-width:200px">{rationale_short}</td>'
            '</tr>'
        )

    if not verdict_rows:
        verdicts_html = '<tr><td colspan="8" style="padding:40px;text-align:center;color:#9ca3af">No verdicts yet. Run the pipeline to generate analysis.</td></tr>'
    else:
        verdicts_html = "\n".join(verdict_rows)

    top_pick = kpi.get("top_pick", "-")
    universe = kpi.get("universe", 0)
    in_debate = kpi.get("in_debate", 0)
    buy_signals = kpi.get("buy_signals", 0)

    # Build the HTML with the search section embedded
    parts = []
    parts.append('<!DOCTYPE html>')
    parts.append('<html lang="en">')
    parts.append('<head>')
    parts.append('  <meta charset="UTF-8">')
    parts.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append('  <title>AgentDesk - Indian Stock Analysis</title>')
    parts.append('  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')
    parts.append('  <style>')
    parts.append('    * { margin: 0; padding: 0; box-sizing: border-box; }')
    parts.append('    body { font-family: \'Inter\', system-ui, -apple-system, sans-serif; background: #f9fafb; color: #111827; line-height: 1.5; }')
    parts.append('    .container { max-width: 1200px; margin: 0 auto; padding: 24px; }')
    parts.append('    header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 16px; }')
    parts.append('    .brand { display: flex; align-items: baseline; gap: 12px; }')
    parts.append('    .brand h1 { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }')
    parts.append('    .brand span { color: #6b7280; font-size: 14px; }')
    parts.append('    .badge { background: #111827; color: #fff; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; }')
    parts.append('    .section-title { font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }')
    parts.append('    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }')
    parts.append('    .kpi-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; }')
    parts.append('    .kpi-label { font-size: 12px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }')
    parts.append('    .kpi-value { font-size: 32px; font-weight: 700; color: #111827; }')
    parts.append('    .kpi-sub { font-size: 13px; color: #6b7280; margin-top: 4px; }')
    parts.append('    .buy-signals { color: #16a34a; }')
    parts.append('    .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 32px; }')
    parts.append('    .agent-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; }')
    parts.append('    .agent-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }')
    parts.append('    .agent-icon { font-size: 20px; }')
    parts.append('    .agent-name { font-weight: 600; font-size: 15px; }')
    parts.append('    .agent-role { font-size: 13px; color: #6b7280; margin-bottom: 12px; }')
    parts.append('    .agent-status { display: inline-flex; align-items: center; gap: 6px; background: #dcfce7; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; color: #16a34a; text-transform: uppercase; }')
    parts.append('    .agent-stats { display: flex; justify-content: space-between; margin-top: 16px; padding-top: 16px; border-top: 1px dashed #e5e7eb; }')
    parts.append('    .agent-stat { text-align: center; }')
    parts.append('    .agent-stat-value { font-size: 20px; font-weight: 700; }')
    parts.append('    .agent-stat-label { font-size: 11px; color: #9ca3af; text-transform: uppercase; margin-top: 2px; }')
    parts.append('    .verdicts-table { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; }')
    parts.append('    .verdicts-table table { width: 100%; border-collapse: collapse; font-size: 14px; }')
    parts.append('    .verdicts-table th { background: #f9fafb; padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }')
    parts.append('    .verdicts-table td { padding: 12px 16px; }')
    parts.append('    .footer { text-align: center; padding: 24px; color: #9ca3af; font-size: 13px; margin-top: 24px; }')
    parts.append('    .timestamp { text-align: right; font-size: 12px; color: #9ca3af; margin-bottom: 16px; }')

    # Search styles
    parts.append('    .search-section { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; margin-bottom: 24px; }')
    parts.append('    .search-title { font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 12px; }')
    parts.append('    .search-box { display: flex; gap: 10px; }')
    parts.append('    .search-input { flex: 1; padding: 12px 16px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 15px; font-family: inherit; outline: none; transition: border-color 0.2s; }')
    parts.append('    .search-input:focus { border-color: #3b82f6; }')
    parts.append('    .search-btn { background: #111827; color: #fff; border: none; padding: 12px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }')
    parts.append('    .search-btn:hover { background: #374151; }')
    parts.append('    .search-btn:disabled { background: #9ca3af; cursor: not-allowed; }')
    parts.append('    .search-hint { font-size: 12px; color: #9ca3af; margin-top: 8px; }')
    parts.append('    .search-error { color: #dc2626; font-size: 13px; margin-top: 8px; display: none; }')
    parts.append('    .search-info { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px 16px; margin-top: 12px; font-size: 13px; color: #1e40af; display: none; }')
    parts.append('    .loading { display: none; text-align: center; padding: 40px; }')
    parts.append('    .loading-spinner { width: 40px; height: 40px; border: 3px solid #e5e7eb; border-top-color: #111827; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }')
    parts.append('    @keyframes spin { to { transform: rotate(360deg); } }')

    # Results styles
    parts.append('    .results { display: none; }')
    parts.append('    .result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }')
    parts.append('    .result-symbol { font-size: 24px; font-weight: 700; }')
    parts.append('    .result-name { color: #6b7280; font-size: 14px; }')
    parts.append('    .result-price { text-align: right; }')
    parts.append('    .result-price-value { font-size: 28px; font-weight: 700; }')
    parts.append('    .result-price-change { font-size: 14px; font-weight: 600; }')
    parts.append('    .positive { color: #16a34a; }')
    parts.append('    .negative { color: #dc2626; }')
    parts.append('    .verdict-banner { padding: 20px; border-radius: 12px; margin-bottom: 24px; text-align: center; }')
    parts.append('    .verdict-banner.buy { background: #dcfce7; border: 2px solid #16a34a; }')
    parts.append('    .verdict-banner.watch { background: #fef3c7; border: 2px solid #ca8a04; }')
    parts.append('    .verdict-banner.avoid { background: #fee2e2; border: 2px solid #dc2626; }')
    parts.append('    .verdict-text { font-size: 32px; font-weight: 700; }')
    parts.append('    .verdict-banner.buy .verdict-text { color: #16a34a; }')
    parts.append('    .verdict-banner.watch .verdict-text { color: #ca8a04; }')
    parts.append('    .verdict-banner.avoid .verdict-text { color: #dc2626; }')
    parts.append('    .verdict-confidence { font-size: 16px; color: #374151; margin-top: 4px; }')
    parts.append('    .verdict-rationale { font-size: 14px; color: #6b7280; margin-top: 8px; max-width: 600px; margin-left: auto; margin-right: auto; }')
    parts.append('    .scores-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }')
    parts.append('    .score-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; }')
    parts.append('    .score-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }')
    parts.append('    .score-icon { font-size: 24px; }')
    parts.append('    .score-name { font-weight: 600; font-size: 15px; }')
    parts.append('    .score-bar-bg { height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; margin-bottom: 8px; }')
    parts.append('    .score-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }')
    parts.append('    .score-value { font-size: 20px; font-weight: 700; }')
    parts.append('    .score-reason { font-size: 12px; color: #6b7280; margin-top: 6px; line-height: 1.4; }')
    parts.append('    .data-table { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; margin-bottom: 24px; }')
    parts.append('    .data-table table { width: 100%; border-collapse: collapse; font-size: 14px; }')
    parts.append('    .data-table th { background: #f9fafb; padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }')
    parts.append('    .data-table td { padding: 12px 16px; border-bottom: 1px solid #f3f4f6; }')
    parts.append('    .data-table tr:last-child td { border-bottom: none; }')

    parts.append('    @media (max-width: 768px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } .agents-grid { grid-template-columns: 1fr; } .verdicts-table { overflow-x: auto; } .verdicts-table table { min-width: 800px; } .scores-grid { grid-template-columns: 1fr; } .search-box { flex-direction: column; } }')
    parts.append('  </style>')
    parts.append('</head>')
    parts.append('<body>')
    parts.append('  <div class="container">')

    # Header
    parts.append('    <header>')
    parts.append('      <div class="brand">')
    parts.append('        <h1>AgentDesk</h1>')
    parts.append('        <span>Indian stock analysis - 8 agents on duty</span>')
    parts.append('      </div>')
    parts.append('      <div class="badge">Live - Auto-Updated</div>')
    parts.append('    </header>')

    # Search Section
    parts.append('    <div class="search-section">')
    parts.append('      <div class="search-title">🔍 Analyze Any Stock (Client-side via Yahoo Finance)</div>')
    parts.append('      <div class="search-box">')
    parts.append('        <input type="text" class="search-input" id="stockInput" placeholder="Enter symbol (e.g., RELIANCE.NS, TCS.NS, INFY.NS)" onkeypress="if(event.key===\'Enter\')analyzeStock()">')
    parts.append('        <button class="search-btn" id="searchBtn" onclick="analyzeStock()">Analyze</button>')
    parts.append('      </div>')
    parts.append('      <div class="search-hint">Try: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, SBIN.NS, ITC.NS</div>')
    parts.append('      <div class="search-error" id="searchError"></div>')
    parts.append('      <div class="search-info" id="searchInfo"></div>')
    parts.append('    </div>')

    # Loading
    parts.append('    <div class="loading" id="loading">')
    parts.append('      <div class="loading-spinner"></div>')
    parts.append('      <div style="color:#6b7280;font-size:14px">Analyzing stock data via Yahoo Finance...</div>')
    parts.append('    </div>')

    # Search Results
    parts.append('    <div class="results" id="results">')
    parts.append('      <div class="result-header">')
    parts.append('        <div>')
    parts.append('          <div class="result-symbol" id="resSymbol">-</div>')
    parts.append('          <div class="result-name" id="resName">-</div>')
    parts.append('        </div>')
    parts.append('        <div class="result-price">')
    parts.append('          <div class="result-price-value" id="resPrice">-</div>')
    parts.append('          <div class="result-price-change" id="resChange">-</div>')
    parts.append('        </div>')
    parts.append('      </div>')
    parts.append('      <div class="verdict-banner" id="verdictBanner">')
    parts.append('        <div class="verdict-text" id="verdictText">-</div>')
    parts.append('        <div class="verdict-confidence" id="verdictConfidence">-</div>')
    parts.append('        <div class="verdict-rationale" id="verdictRationale">-</div>')
    parts.append('      </div>')
    parts.append('      <div class="section-title">Agent Scores</div>')
    parts.append('      <div class="scores-grid" id="scoresGrid"></div>')
    parts.append('      <div class="section-title">Key Metrics</div>')
    parts.append('      <div class="data-table">')
    parts.append('        <table>')
    parts.append('          <thead><tr><th>Metric</th><th>Value</th></tr></thead>')
    parts.append('          <tbody id="metricsBody"></tbody>')
    parts.append('        </table>')
    parts.append('      </div>')
    parts.append('    </div>')

    # Pipeline results
    parts.append(f'    <div class="timestamp">Last updated: {timestamp} - Engine: {engine}</div>')
    parts.append('    <div class="section-title">Overview</div>')
    parts.append('    <div class="kpi-grid">')
    parts.append(f'      <div class="kpi-card"><div class="kpi-label">Universe</div><div class="kpi-value">{universe}</div><div class="kpi-sub">stocks screened</div></div>')
    parts.append(f'      <div class="kpi-card"><div class="kpi-label">In Debate</div><div class="kpi-value">{in_debate}</div><div class="kpi-sub">shortlisted for analysis</div></div>')
    parts.append(f'      <div class="kpi-card"><div class="kpi-label">Buy Signals</div><div class="kpi-value buy-signals">{buy_signals}</div><div class="kpi-sub">{buy_count} BUY - {watch_count} WATCH - {avoid_count} AVOID</div></div>')
    parts.append(f'      <div class="kpi-card"><div class="kpi-label">Top Pick</div><div class="kpi-value" style="font-size:20px">{top_pick}</div><div class="kpi-sub">highest confidence</div></div>')
    parts.append('    </div>')

    # Agent Panel
    parts.append('    <div class="section-title">Agent Panel</div>')
    parts.append('    <div class="agents-grid">')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#128301;</span><span class="agent-name">Scout</span></div><div class="agent-role">screens the stock universe for movers</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{universe}</div><div class="agent-stat-label">Scanned</div></div><div class="agent-stat"><div class="agent-stat-value">{in_debate}</div><div class="agent-stat-label">Shortlisted</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#128200;</span><span class="agent-name">Technician</span></div><div class="agent-role">reads price action, RVOL and trend</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{in_debate}</div><div class="agent-stat-label">Analyzed</div></div><div class="agent-stat"><div class="agent-stat-value">-</div><div class="agent-stat-label">Avg RVOL</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#129518;</span><span class="agent-name">Fundamentalist</span></div><div class="agent-role">weighs valuation and analyst targets</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{in_debate}</div><div class="agent-stat-label">Covered</div></div><div class="agent-stat"><div class="agent-stat-value">-</div><div class="agent-stat-label">Avg Upside</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#128240;</span><span class="agent-name">Newsdesk</span></div><div class="agent-role">pulls live news and scores sentiment</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">-</div><div class="agent-stat-label">Headlines</div></div><div class="agent-stat"><div class="agent-stat-value">-</div><div class="agent-stat-label">Net Tone</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#128002;</span><span class="agent-name">Bull</span></div><div class="agent-role">argues the case to buy</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{in_debate}</div><div class="agent-stat-label">Cases</div></div><div class="agent-stat"><div class="agent-stat-value">-</div><div class="agent-stat-label">Avg Score</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#128059;</span><span class="agent-name">Bear</span></div><div class="agent-role">argues the case against</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{in_debate}</div><div class="agent-stat-label">Cases</div></div><div class="agent-stat"><div class="agent-stat-value">-</div><div class="agent-stat-label">Avg Score</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#9878;</span><span class="agent-name">Judge</span></div><div class="agent-role">weighs the debate, issues verdict + confidence</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{in_debate}</div><div class="agent-stat-label">Verdicts</div></div><div class="agent-stat"><div class="agent-stat-value" style="color:#16a34a">{buy_signals}</div><div class="agent-stat-label">Buy</div></div></div></div>')
    parts.append(f'      <div class="agent-card"><div class="agent-header"><span class="agent-icon">&#128235;</span><span class="agent-name">Messenger</span></div><div class="agent-role">sends signals to Telegram</div><span class="agent-status">&#9679; Done</span><div class="agent-stats"><div class="agent-stat"><div class="agent-stat-value">{buy_signals}</div><div class="agent-stat-label">Sent</div></div><div class="agent-stat"><div class="agent-stat-value" style="font-size:14px">{engine}</div><div class="agent-stat-label">Engine</div></div></div></div>')
    parts.append('    </div>')

    # Verdicts table
    parts.append(f'    <div class="section-title">Latest Verdicts ({len(verdicts)})</div>')
    parts.append('    <div class="verdicts-table">')
    parts.append('      <table>')
    parts.append('        <thead><tr><th>Symbol</th><th>Name</th><th>Verdict</th><th style="text-align:center">Conf</th><th>Winner</th><th>Price</th><th>Change</th><th>Rationale</th></tr></thead>')
    parts.append('        <tbody>')
    parts.append(verdicts_html)
    parts.append('        </tbody>')
    parts.append('      </table>')
    parts.append('    </div>')

    # Footer
    parts.append('    <div class="footer">')
    parts.append(f'      Built from {universe} real stocks - data pulled {timestamp} - engine: {engine}<br>')
    parts.append('      <span style="color:#9ca3af;font-size:12px">Analysis only. No trade was placed. Not investment advice.</span>')
    parts.append('    </div>')
    parts.append('  </div>')

    # JavaScript for client-side search
    parts.append('  <script>')
    parts.append('    function showLoading() { document.getElementById("loading").style.display = "block"; document.getElementById("results").style.display = "none"; document.getElementById("searchError").style.display = "none"; document.getElementById("searchInfo").style.display = "none"; document.getElementById("searchBtn").disabled = true; }')
    parts.append('    function hideLoading() { document.getElementById("loading").style.display = "none"; document.getElementById("searchBtn").disabled = false; }')
    parts.append('    function showError(msg) { var el = document.getElementById("searchError"); el.textContent = msg; el.style.display = "block"; hideLoading(); }')
    parts.append('    function showInfo(msg) { var el = document.getElementById("searchInfo"); el.textContent = msg; el.style.display = "block"; }')

    parts.append('    async function analyzeStock() {')
    parts.append('      var raw = document.getElementById("stockInput").value.trim().toUpperCase();')
    parts.append('      if (!raw) { showError("Please enter a stock symbol"); return; }')
    parts.append('      var symbol = raw; if (!symbol.includes(".")) symbol = symbol + ".NS";')
    parts.append('      showLoading(); showInfo("Fetching data from Yahoo Finance...");')
    parts.append('      try {')
    parts.append('        var proxyUrl = "https://api.allorigins.win/raw?url=";')
    parts.append('        var yahooUrl = encodeURIComponent("https://query1.finance.yahoo.com/v8/finance/chart/" + symbol + "?interval=1d&range=1mo");')
    parts.append('        var res = await fetch(proxyUrl + yahooUrl);')
    parts.append('        if (!res.ok) throw new Error("Failed to fetch stock data");')
    parts.append('        var data = await res.json();')
    parts.append('        if (!data.chart || !data.chart.result || data.chart.result.length === 0) {')
    parts.append('          showError("Could not find data for " + symbol + ". Try adding .NS (e.g., RELIANCE.NS)"); return;')
    parts.append('        }')
    parts.append('        var result = data.chart.result[0];')
    parts.append('        var meta = result.meta;')
    parts.append('        var quotes = result.indicators.quote[0];')
    parts.append('        var live = meta.regularMarketPrice || meta.previousClose;')
    parts.append('        var prevClose = meta.previousClose || meta.chartPreviousClose;')
    parts.append('        var dayChange = prevClose ? ((live - prevClose) / prevClose * 100).toFixed(2) : 0;')
    parts.append('        var volume = meta.regularMarketVolume || 0;')
    parts.append('        var closes = quotes.close.filter(function(c){return c!==null;});')
    parts.append('        var volumes = quotes.volume.filter(function(v){return v!==null;});')
    parts.append('        var highs = quotes.high.filter(function(h){return h!==null;});')
    parts.append('        var lows = quotes.low.filter(function(l){return l!==null;});')
    parts.append('        var sma20 = closes.length >= 20 ? closes.slice(-20).reduce(function(a,b){return a+b;},0)/20 : null;')
    parts.append('        var priceVsSma = sma20 ? ((live - sma20) / sma20 * 100).toFixed(2) : null;')
    parts.append('        var hi52 = meta.fiftyTwoWeekHigh || Math.max.apply(null, highs);')
    parts.append('        var lo52 = meta.fiftyTwoWeekLow || Math.min.apply(null, lows);')
    parts.append('        var pos52 = hi52 && lo52 ? (((live - lo52) / (hi52 - lo52)) * 100).toFixed(1) : null;')
    parts.append('        var todayVol = volumes[volumes.length-1] || 0;')
    parts.append('        var avgVol = volumes.slice(0,-1).length > 0 ? volumes.slice(0,-1).reduce(function(a,b){return a+b;},0)/volumes.slice(0,-1).length : todayVol;')
    parts.append('        var rvol = avgVol > 0 ? (todayVol / avgVol).toFixed(2) : 1;')
    parts.append('        var trend = priceVsSma > 1 ? "up" : priceVsSma < -1 ? "down" : "sideways";')
    parts.append('        var evidence = {')
    parts.append('          symbol: symbol, name: meta.shortName || meta.longName || symbol,')
    parts.append('          price: {live: live, day_change_pct: parseFloat(dayChange), volume: volume},')
    parts.append('          technicals: {rvol: parseFloat(rvol), price_vs_sma_pct: priceVsSma ? parseFloat(priceVsSma) : null, trend: trend},')
    parts.append('          range_52w: {high: hi52, low: lo52, position_pct: pos52 ? parseFloat(pos52) : null},')
    parts.append('          analyst: {target_mean: meta.targetMeanPrice || null, upside_pct: null, consensus: null},')
    parts.append('          news: {total: 0, positive: 0, negative: 0}')
    parts.append('        };')
    parts.append('        var result_scores = evaluateDeterministic(evidence);')
    parts.append('        renderResults(evidence, result_scores);')
    parts.append('      } catch(e) { showError("Failed: " + e.message); console.error(e); }')
    parts.append('    }')

    parts.append('    function evaluateDeterministic(ev) {')
    parts.append('      var bullScore = 0, bearScore = 0;')
    parts.append('      var bullReasons = [], bearReasons = [];')
    parts.append('      var rvol = ev.technicals.rvol;')
    parts.append('      if (rvol > 1.5) { bullScore += 25; bullReasons.push("RVOL " + rvol + "x — strong volume"); }')
    parts.append('      else if (rvol < 0.8) { bearScore += 15; bearReasons.push("RVOL " + rvol + "x — weak participation"); }')
    parts.append('      var pos52 = ev.range_52w.position_pct;')
    parts.append('      if (pos52 >= 80) { bullScore += 20; bullReasons.push("Near 52w high (" + pos52 + "%)"); }')
    parts.append('      else if (pos52 <= 25) { bearScore += 20; bearReasons.push("Near 52w low (" + pos52 + "%)"); }')
    parts.append('      var sma = ev.technicals.price_vs_sma_pct;')
    parts.append('      if (sma > 1) { bullScore += 15; bullReasons.push("Trading " + sma + "% above SMA"); }')
    parts.append('      else if (sma < -1) { bearScore += 15; bearReasons.push("Trading " + sma + "% below SMA"); }')
    parts.append('      var change = ev.price.day_change_pct;')
    parts.append('      if (change > 2) { bullScore += 10; bullReasons.push("Strong day move +" + change + "%"); }')
    parts.append('      else if (change < -2) { bearScore += 10; bearReasons.push("Weak day move " + change + "%"); }')
    parts.append('      bullScore = Math.min(100, bullScore); bearScore = Math.min(100, bearScore);')
    parts.append('      if (bullReasons.length === 0) bullReasons.push("No strong bullish signals");')
    parts.append('      if (bearReasons.length === 0) bearReasons.push("No strong bearish signals");')
    parts.append('      var net = bullScore - bearScore;')
    parts.append('      var leadership = (pos52 >= 60) || (rvol >= 2);')
    parts.append('      var verdict, confidence;')
    parts.append('      if (net >= 20 && leadership) { verdict = "BUY"; confidence = Math.max(7, Math.min(10, Math.round(5 + net/15))); }')
    parts.append('      else if (net <= -15) { verdict = "AVOID"; confidence = Math.max(1, Math.min(6, Math.round(5 + net/15))); }')
    parts.append('      else { verdict = "WATCH"; confidence = Math.max(1, Math.min(10, Math.round(5 + net/15))); }')
    parts.append('      return {')
    parts.append('        scores: {')
    parts.append('          bull: {score: bullScore, reasons: bullReasons},')
    parts.append('          bear: {score: bearScore, reasons: bearReasons},')
    parts.append('          technician: {score: Math.min(100, 50 + (sma||0)*2 + (rvol-1)*10), reasons: ["RVOL " + rvol + "x", "Trend: " + ev.technicals.trend]},')
    parts.append('          fundamentalist: {score: 50, reasons: ["No analyst data in client mode"]},')
    parts.append('          newsdesk: {score: 50, reasons: ["No news data in client mode"]}')
    parts.append('        },')
    parts.append('        verdict: {')
    parts.append('          verdict: verdict, confidence: confidence,')
    parts.append('          winner: bullScore >= bearScore ? "Bull" : "Bear",')
    parts.append('          rationale: net >= 20 ? "Bull case leads (net " + net + ") with momentum." : net <= -15 ? "Bear case dominates (net " + net + ")." : "Mixed picture (net " + net + "); no clear edge.",')
    parts.append('          key_catalyst: bullScore >= bearScore ? bullReasons[0] : bearReasons[0],')
    parts.append('          bull_score: bullScore, bear_score: bearScore, net: net')
    parts.append('        }')
    parts.append('      };')
    parts.append('    }')

    parts.append('    function renderResults(ev, result) {')
    parts.append('      document.getElementById("resSymbol").textContent = ev.symbol;')
    parts.append('      document.getElementById("resName").textContent = ev.name;')
    parts.append('      var price = ev.price;')
    parts.append('      document.getElementById("resPrice").textContent = "₹" + price.live.toFixed(2);')
    parts.append('      var change = price.day_change_pct;')
    parts.append('      var chgEl = document.getElementById("resChange");')
    parts.append('      chgEl.textContent = (change >= 0 ? "+" : "") + change + "%";')
    parts.append('      chgEl.className = "result-price-change " + (change >= 0 ? "positive" : "negative");')
    parts.append('      var v = result.verdict;')
    parts.append('      var banner = document.getElementById("verdictBanner");')
    parts.append('      banner.className = "verdict-banner " + v.verdict.toLowerCase();')
    parts.append('      document.getElementById("verdictText").textContent = v.verdict;')
    parts.append('      document.getElementById("verdictConfidence").textContent = "Confidence: " + v.confidence + "/10 · Winner: " + v.winner;')
    parts.append('      document.getElementById("verdictRationale").textContent = v.rationale;')
    parts.append('      var scores = result.scores;')
    parts.append('      var cfg = [')
    parts.append('        {key:"bull", icon:"🐂", name:"Bull", color:"#16a34a"},')
    parts.append('        {key:"bear", icon:"🐻", name:"Bear", color:"#dc2626"},')
    parts.append('        {key:"technician", icon:"📈", name:"Technician", color:"#3b82f6"},')
    parts.append('        {key:"fundamentalist", icon:"🧮", name:"Fundamentalist", color:"#8b5cf6"},')
    parts.append('        {key:"newsdesk", icon:"📰", name:"Newsdesk", color:"#f59e0b"}')
    parts.append('      ];')
    parts.append('      document.getElementById("scoresGrid").innerHTML = cfg.map(function(c){')
    parts.append('        var s = scores[c.key] || {score:0, reasons:["No data"]};')
    parts.append('        return \'<div class="score-card"><div class="score-header"><span class="score-icon">\' + c.icon + \'</span><span class="score-name">\' + c.name + \'</span></div><div class="score-bar-bg"><div class="score-bar-fill" style="width:\' + Math.max(0,Math.min(100,s.score)) + \'%;background:\' + c.color + \'"></div></div><div class="score-value" style="color:\' + c.color + \'">\' + s.score + \'/100</div><div class="score-reason">\' + ((s.reasons && s.reasons[0]) || "") + \'</div></div>\';')
    parts.append('      }).join("");')
    parts.append('      document.getElementById("metricsBody").innerHTML = "<tr><td>Current Price</td><td>₹" + price.live.toFixed(2) + "</td></tr><tr><td>Day Change</td><td class=\\"" + (change >= 0 ? "positive" : "negative") + "\\">" + (change >= 0 ? "+" : "") + change + "%</td></tr><tr><td>Volume</td><td>" + price.volume.toLocaleString() + "</td></tr><tr><td>RVOL</td><td>" + ev.technicals.rvol + "x</td></tr><tr><td>Trend</td><td>" + ev.technicals.trend + "</td></tr><tr><td>Price vs SMA</td><td>" + (ev.technicals.price_vs_sma_pct != null ? ev.technicals.price_vs_sma_pct + "%" : "-") + "</td></tr><tr><td>52W High</td><td>₹" + (ev.range_52w.high ? ev.range_52w.high.toFixed(2) : "-") + "</td></tr><tr><td>52W Low</td><td>₹" + (ev.range_52w.low ? ev.range_52w.low.toFixed(2) : "-") + "</td></tr><tr><td>52W Position</td><td>" + (ev.range_52w.position_pct != null ? ev.range_52w.position_pct + "%" : "-") + "</td></tr><tr><td>Analyst Target</td><td>" + (ev.analyst.target_mean ? "₹" + ev.analyst.target_mean : "— (client mode)") + "</td></tr><tr><td>Engine</td><td>Client-side deterministic</td></tr>";')
    parts.append('      document.getElementById("results").style.display = "block";')
    parts.append('      hideLoading();')
    parts.append('      document.getElementById("results").scrollIntoView({behavior:"smooth", block:"start"});')
    parts.append('    }')
    parts.append('  </script>')
    parts.append('</body>')
    parts.append('</html>')

    return "\n".join(parts)

def main():
    data = load_output()
    html = generate_static_html(data)

    os.makedirs("_site", exist_ok=True)
    with open(STATIC_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Static dashboard generated: {STATIC_INDEX_PATH}")
    print(f"   Universe: {data['kpi'].get('universe', 0)} stocks")
    print(f"   Verdicts: {len(data.get('verdicts', []))}")
    print(f"   BUY signals: {data['kpi'].get('buy_signals', 0)}")
    print(f"   ✅ Includes client-side stock search!")

if __name__ == "__main__":
    main()