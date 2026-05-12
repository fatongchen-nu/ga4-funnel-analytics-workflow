"""Build a self-contained HTML dashboard from the metric evidence layer."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def as_number(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def normalize_opportunity_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    numeric_fields = [
        "eligible_sessions",
        "begin_checkout_sessions",
        "purchase_sessions",
        "revenue",
        "segment_conversion_rate",
        "benchmark_conversion_rate",
        "conversion_rate_gap",
        "average_order_value",
        "estimated_missed_conversions",
        "estimated_revenue_opportunity",
    ]
    normalized = []
    for row in rows:
        item = dict(row)
        item["segment_name"] = f"{row['user_source']} / {row['user_medium']} / {row['device_category']}"
        for field in numeric_fields:
            item[field] = as_number(row.get(field))
        normalized.append(item)
    return normalized


def html_template(payload: dict[str, Any]) -> str:
    data_json = json.dumps(payload, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GA4 Funnel Analytics Dashboard</title>
  <style>
    :root {{
      --bg: #f6f5f1;
      --panel: #ffffff;
      --ink: #181b1f;
      --muted: #626b76;
      --line: #d9ddd8;
      --teal: #007c89;
      --green: #4f8a5b;
      --amber: #c57b18;
      --red: #c4493d;
      --violet: #6d5bd0;
      --shadow: 0 16px 44px rgba(31, 35, 39, 0.10);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}

    button, input, select {{
      font: inherit;
    }}

    .app-shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
    }}

    aside {{
      position: sticky;
      top: 0;
      height: 100vh;
      padding: 22px;
      border-right: 1px solid var(--line);
      background: #eeede7;
      overflow: auto;
    }}

    main {{
      min-width: 0;
      padding: 28px;
    }}

    .brand {{
      display: grid;
      gap: 8px;
      margin-bottom: 28px;
    }}

    .brand-mark {{
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      background: var(--ink);
      color: white;
      font-weight: 800;
    }}

    h1, h2, h3, p {{
      margin: 0;
    }}

    h1 {{
      max-width: 980px;
      font-size: clamp(32px, 5vw, 66px);
      line-height: 0.95;
      letter-spacing: 0;
    }}

    h2 {{
      font-size: 20px;
      line-height: 1.2;
    }}

    h3 {{
      font-size: 14px;
      line-height: 1.25;
    }}

    .muted {{
      color: var(--muted);
    }}

    .small {{
      font-size: 12px;
      line-height: 1.45;
    }}

    .nav {{
      display: grid;
      gap: 8px;
      margin: 22px 0;
    }}

    .nav a {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--ink);
      text-decoration: none;
      padding: 10px 12px;
      border-radius: 8px;
    }}

    .nav a:hover {{
      background: rgba(0, 124, 137, 0.10);
    }}

    .dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--teal);
    }}

    .controls {{
      display: grid;
      gap: 14px;
      padding-top: 20px;
      border-top: 1px solid var(--line);
    }}

    label {{
      display: grid;
      gap: 6px;
      font-size: 12px;
      color: var(--muted);
    }}

    input[type="search"], select {{
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      color: var(--ink);
      padding: 8px 10px;
    }}

    input[type="range"] {{
      width: 100%;
      accent-color: var(--teal);
    }}

    .toggle-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }}

    .toggle-row input {{
      width: 18px;
      height: 18px;
      accent-color: var(--teal);
    }}

    .hero {{
      display: grid;
      gap: 22px;
      padding-bottom: 22px;
      border-bottom: 1px solid var(--line);
    }}

    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}

    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 30px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.76);
      padding: 6px 9px;
      color: var(--muted);
      font-size: 12px;
    }}

    .section {{
      padding: 26px 0;
      border-bottom: 1px solid var(--line);
    }}

    .section-head {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 16px;
    }}

    .grid {{
      display: grid;
      gap: 14px;
    }}

    .kpis {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}

    .two-col {{
      grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
      align-items: start;
    }}

    .panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
      min-width: 0;
    }}

    .panel-pad {{
      padding: 18px;
    }}

    .kpi {{
      display: grid;
      gap: 12px;
      min-height: 136px;
    }}

    .kpi-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}

    .kpi-value {{
      font-size: 28px;
      line-height: 1.05;
      font-weight: 780;
      overflow-wrap: anywhere;
    }}

    .badge {{
      padding: 4px 7px;
      border-radius: 8px;
      font-size: 11px;
      border: 1px solid var(--line);
      color: var(--muted);
      background: #fafafa;
      white-space: nowrap;
    }}

    .funnel {{
      display: grid;
      gap: 12px;
    }}

    .funnel-row {{
      display: grid;
      grid-template-columns: 130px minmax(0, 1fr) 92px;
      gap: 12px;
      align-items: center;
    }}

    .bar-track {{
      position: relative;
      height: 42px;
      border-radius: 8px;
      background: #ecefea;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      min-width: 2px;
      border-radius: 8px;
      background: linear-gradient(90deg, var(--teal), var(--green));
      transition: width 240ms ease, filter 180ms ease;
    }}

    .bar-track:hover .bar-fill {{
      filter: brightness(0.92);
    }}

    .dropoff {{
      color: var(--red);
      font-weight: 740;
      text-align: right;
    }}

    .insight {{
      border-left: 4px solid var(--amber);
      background: #fff8ee;
      padding: 16px;
      border-radius: 8px;
      display: grid;
      gap: 10px;
    }}

    .opportunity-list {{
      display: grid;
      gap: 10px;
      max-height: 596px;
      overflow: auto;
      padding-right: 4px;
    }}

    .segment-row {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      display: grid;
      gap: 10px;
      background: white;
      cursor: pointer;
    }}

    .segment-row.active {{
      border-color: var(--teal);
      box-shadow: inset 0 0 0 1px var(--teal);
    }}

    .segment-title {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }}

    .mini-bar {{
      height: 8px;
      border-radius: 8px;
      background: #ecefea;
      overflow: hidden;
    }}

    .mini-bar span {{
      display: block;
      height: 100%;
      border-radius: 8px;
      background: var(--violet);
    }}

    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}

    .metric-box {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfbfa;
      min-height: 86px;
    }}

    .metric-box strong {{
      display: block;
      font-size: 20px;
      margin-top: 7px;
      overflow-wrap: anywhere;
    }}

    .scenario {{
      display: grid;
      gap: 12px;
      margin-top: 14px;
    }}

    .slider-line {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
    }}

    .evidence {{
      display: none;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px dashed var(--line);
      color: var(--muted);
      font-size: 11px;
      overflow-wrap: anywhere;
    }}

    body.show-evidence .evidence {{
      display: block;
    }}

    .table-wrap {{
      overflow: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}

    th, td {{
      padding: 11px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}

    th {{
      position: sticky;
      top: 0;
      background: white;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
    }}

    .footer {{
      padding: 24px 0 10px;
      color: var(--muted);
    }}

    @media (max-width: 1020px) {{
      .app-shell {{
        grid-template-columns: 1fr;
      }}

      aside {{
        position: relative;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--line);
      }}

      .kpis, .two-col {{
        grid-template-columns: 1fr;
      }}

      main {{
        padding: 20px;
      }}
    }}

    @media (max-width: 620px) {{
      .funnel-row {{
        grid-template-columns: 1fr;
      }}

      .dropoff {{
        text-align: left;
      }}

      .detail-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    <aside>
      <div class="brand">
        <div class="brand-mark">GA4</div>
        <div>
          <h2>Funnel Analytics</h2>
          <p class="small muted">Evidence-backed ecommerce opportunity dashboard</p>
        </div>
      </div>
      <nav class="nav" aria-label="Dashboard sections">
        <a href="#overview"><span class="dot"></span>Overview</a>
        <a href="#funnel"><span class="dot" style="background: var(--green)"></span>Funnel</a>
        <a href="#opportunity"><span class="dot" style="background: var(--violet)"></span>Opportunity</a>
        <a href="#experiment"><span class="dot" style="background: var(--amber)"></span>Experiment</a>
      </nav>
      <div class="controls" aria-label="Dashboard controls">
        <label>
          Segment search
          <input id="segmentSearch" type="search" placeholder="google organic desktop">
        </label>
        <label>
          Device filter
          <select id="deviceFilter">
            <option value="all">All devices</option>
          </select>
        </label>
        <label>
          Sort opportunities
          <select id="sortMode">
            <option value="estimated_revenue_opportunity">Revenue opportunity</option>
            <option value="estimated_missed_conversions">Missed conversions</option>
            <option value="conversion_rate_gap">Conversion gap</option>
            <option value="eligible_sessions">Eligible sessions</option>
          </select>
        </label>
        <div class="toggle-row">
          <span class="small muted">Show evidence paths</span>
          <input id="evidenceToggle" type="checkbox" aria-label="Show evidence source paths">
        </div>
      </div>
    </aside>

    <main>
      <section id="overview" class="hero">
        <div class="hero-meta">
          <span class="chip">Source: GA4 BigQuery public sample</span>
          <span class="chip" id="periodChip"></span>
          <span class="chip">Generated by SQL/Python</span>
        </div>
        <h1>Where the ecommerce funnel loses intent, and which segment is worth investigating first.</h1>
        <p class="muted">This dashboard is generated from deterministic metric evidence. Narrative labels and recommendations point back to the evidence packet instead of inventing numbers.</p>
        <div class="grid kpis" id="kpiGrid"></div>
      </section>

      <section id="funnel" class="section">
        <div class="section-head">
          <div>
            <h2>Funnel Drop-Off</h2>
            <p class="small muted">Session-level progression across ecommerce events.</p>
          </div>
          <span class="badge" id="topDropoffBadge"></span>
        </div>
        <div class="grid two-col">
          <div class="panel panel-pad">
            <div class="funnel" id="funnelChart"></div>
          </div>
          <div class="insight">
            <h3>Interpretation</h3>
            <p id="funnelNarrative"></p>
            <p class="small muted">Potential causes are hypotheses only. Validating product-page content, CTA clarity, pricing cues, inventory visibility, and merchandising requires additional evidence.</p>
            <div class="evidence">metric_evidence_packet.funnel</div>
          </div>
        </div>
      </section>

      <section id="opportunity" class="section">
        <div class="section-head">
          <div>
            <h2>Segment Opportunity</h2>
            <p class="small muted">Ranked by counterfactual revenue opportunity against the overall checkout-to-purchase benchmark.</p>
          </div>
          <span class="badge" id="segmentCountBadge"></span>
        </div>
        <div class="grid two-col">
          <div class="panel panel-pad">
            <div class="opportunity-list" id="opportunityList"></div>
          </div>
          <div class="panel panel-pad">
            <h3 id="selectedSegmentTitle">Selected segment</h3>
            <p class="small muted" id="selectedSegmentSubtitle"></p>
            <div class="detail-grid" id="segmentDetails"></div>
            <div class="scenario">
              <div class="slider-line">
                <h3>Target conversion scenario</h3>
                <span class="badge" id="targetRateLabel"></span>
              </div>
              <input id="targetRate" type="range" min="0" max="100" step="0.1">
              <div class="detail-grid" id="scenarioDetails"></div>
            </div>
            <div class="evidence">metric_evidence_packet.opportunity and ga4_funnel_portfolio.opportunity_inputs</div>
          </div>
        </div>
      </section>

      <section id="experiment" class="section">
        <div class="section-head">
          <div>
            <h2>Experiment Feasibility</h2>
            <p class="small muted">The sample-size estimate is a traffic check, not an automatic recommendation to launch.</p>
          </div>
          <span class="badge">Traffic sufficiency warning</span>
        </div>
        <div class="grid two-col">
          <div class="panel panel-pad">
            <div class="detail-grid" id="experimentDetails"></div>
          </div>
          <div class="insight">
            <h3>Decision note</h3>
            <p id="experimentNarrative"></p>
            <p class="small muted" id="experimentNextStep"></p>
            <div class="evidence">metric_evidence_packet.experiment_feasibility</div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div>
            <h2>Top Opportunity Table</h2>
            <p class="small muted">Filtered by the controls in the left rail.</p>
          </div>
        </div>
        <div class="panel table-wrap">
          <table>
            <thead>
              <tr>
                <th>Segment</th>
                <th>CVR</th>
                <th>Benchmark</th>
                <th>Gap</th>
                <th>Missed conv.</th>
                <th>Revenue opp.</th>
              </tr>
            </thead>
            <tbody id="opportunityTable"></tbody>
          </table>
        </div>
      </section>

      <p class="footer small">Generated from outputs/metric_evidence_packet.json and deterministic SQL/Python exports. Public GA4 sample data is obfuscated, so placeholder values such as &lt;Other&gt; or (data deleted) may appear.</p>
    </main>
  </div>

  <script id="dashboard-data" type="application/json">{data_json}</script>
  <script>
    const data = JSON.parse(document.getElementById('dashboard-data').textContent);
    const packet = data.packet;
    const opportunities = data.opportunities;

    const fmtInt = new Intl.NumberFormat('en-US', {{ maximumFractionDigits: 0 }});
    const fmtOne = new Intl.NumberFormat('en-US', {{ maximumFractionDigits: 1 }});
    const fmtMoney = new Intl.NumberFormat('en-US', {{ style: 'currency', currency: 'USD', maximumFractionDigits: 0 }});
    const pct = (value) => value == null ? 'n/a' : `${{fmtOne.format(value * 100)}}%`;
    const num = (value) => value == null ? 'n/a' : fmtInt.format(value);
    const money = (value) => value == null ? 'n/a' : fmtMoney.format(value);

    let selectedSegment = packet.opportunity.segment_name;

    function metricCard(label, value, badge, source) {{
      return `
        <div class="panel panel-pad kpi">
          <div class="kpi-top">
            <h3>${{label}}</h3>
            <span class="badge">${{badge}}</span>
          </div>
          <div class="kpi-value">${{value}}</div>
          <div class="evidence">${{source}}</div>
        </div>
      `;
    }}

    function renderKpis() {{
      const p = packet.project;
      const f = packet.funnel;
      const o = packet.opportunity;
      document.getElementById('periodChip').textContent = `Period: ${{p.analysis_period_label}}`;
      document.getElementById('kpiGrid').innerHTML = [
        metricCard('Events analyzed', num(p.event_count), 'Scale', 'metric_evidence_packet.project.event_count'),
        metricCard('Top drop-off', f.top_dropoff_step.replaceAll('_', ' -> '), pct(f.top_dropoff_rate), 'metric_evidence_packet.funnel.top_dropoff_step'),
        metricCard('Top opportunity', o.segment_name, 'Segment', 'metric_evidence_packet.opportunity.segment_name'),
        metricCard('Revenue opportunity', money(o.estimated_revenue_opportunity), `${{fmtOne.format(o.estimated_missed_conversions)}} missed conv.`, 'metric_evidence_packet.opportunity.estimated_revenue_opportunity')
      ].join('');
      document.getElementById('topDropoffBadge').textContent = `${{pct(f.top_dropoff_rate)}} drop-off`;
    }}

    function renderFunnel() {{
      const steps = packet.funnel.funnel_steps;
      const maxSessions = Math.max(...steps.map(step => step.sessions || 0));
      document.getElementById('funnelChart').innerHTML = steps.map(step => {{
        const width = ((step.sessions || 0) / maxSessions) * 100;
        return `
          <div class="funnel-row">
            <div>
              <strong>${{step.step.replaceAll('_', ' ')}}</strong>
              <div class="small muted">${{num(step.sessions)}} sessions</div>
            </div>
            <div class="bar-track" title="${{num(step.sessions)}} sessions">
              <div class="bar-fill" style="width: ${{width}}%"></div>
            </div>
            <div class="dropoff">${{step.dropoff_rate == null ? '' : pct(step.dropoff_rate)}}</div>
          </div>
        `;
      }}).join('');
      document.getElementById('funnelNarrative').textContent =
        `The largest observed break is ${{packet.funnel.top_dropoff_step.replaceAll('_', ' -> ')}}, where ${{pct(packet.funnel.top_dropoff_rate)}} of sessions fail to reach the next funnel step.`;
    }}

    function currentFilteredOpportunities() {{
      const query = document.getElementById('segmentSearch').value.trim().toLowerCase();
      const device = document.getElementById('deviceFilter').value;
      const sort = document.getElementById('sortMode').value;
      return opportunities
        .filter(row => device === 'all' || row.device_category === device)
        .filter(row => !query || row.segment_name.toLowerCase().includes(query))
        .sort((a, b) => (b[sort] || 0) - (a[sort] || 0));
    }}

    function renderDeviceOptions() {{
      const devices = Array.from(new Set(opportunities.map(row => row.device_category))).sort();
      document.getElementById('deviceFilter').innerHTML = '<option value="all">All devices</option>' +
        devices.map(device => `<option value="${{device}}">${{device}}</option>`).join('');
    }}

    function renderOpportunityList() {{
      const rows = currentFilteredOpportunities();
      const maxRevenue = Math.max(...opportunities.map(row => row.estimated_revenue_opportunity || 0), 1);
      if (!rows.some(row => row.segment_name === selectedSegment) && rows[0]) {{
        selectedSegment = rows[0].segment_name;
      }}
      document.getElementById('segmentCountBadge').textContent = `${{rows.length}} segments`;
      document.getElementById('opportunityList').innerHTML = rows.slice(0, 18).map(row => {{
        const active = row.segment_name === selectedSegment ? ' active' : '';
        const width = ((row.estimated_revenue_opportunity || 0) / maxRevenue) * 100;
        return `
          <button class="segment-row${{active}}" data-segment="${{row.segment_name}}">
            <div class="segment-title">
              <strong>${{row.segment_name}}</strong>
              <span class="badge">${{money(row.estimated_revenue_opportunity)}}</span>
            </div>
            <div class="mini-bar"><span style="width: ${{width}}%"></span></div>
            <div class="small muted">CVR ${{pct(row.segment_conversion_rate)}} vs benchmark ${{pct(row.benchmark_conversion_rate)}} · ${{fmtOne.format(row.estimated_missed_conversions || 0)}} missed conversions</div>
          </button>
        `;
      }}).join('');
      document.querySelectorAll('.segment-row').forEach(button => {{
        button.addEventListener('click', () => {{
          selectedSegment = button.dataset.segment;
          renderOpportunityList();
          renderSelectedSegment();
          renderOpportunityTable();
        }});
      }});
      renderSelectedSegment();
      renderOpportunityTable();
    }}

    function selectedRow() {{
      return opportunities.find(row => row.segment_name === selectedSegment) || opportunities[0];
    }}

    function metricBox(label, value, source) {{
      return `<div class="metric-box"><span class="small muted">${{label}}</span><strong>${{value}}</strong><div class="evidence">${{source}}</div></div>`;
    }}

    function renderSelectedSegment() {{
      const row = selectedRow();
      if (!row) return;
      document.getElementById('selectedSegmentTitle').textContent = row.segment_name;
      document.getElementById('selectedSegmentSubtitle').textContent = `${{num(row.eligible_sessions)}} eligible sessions · ${{num(row.begin_checkout_sessions)}} checkout entrants · ${{num(row.purchase_sessions)}} purchases`;
      document.getElementById('segmentDetails').innerHTML = [
        metricBox('Segment CVR', pct(row.segment_conversion_rate), 'segment_conversion_rate'),
        metricBox('Benchmark CVR', pct(row.benchmark_conversion_rate), 'benchmark_conversion_rate'),
        metricBox('Conversion gap', pct(row.conversion_rate_gap), 'conversion_rate_gap'),
        metricBox('Revenue opportunity', money(row.estimated_revenue_opportunity), 'estimated_revenue_opportunity')
      ].join('');

      const slider = document.getElementById('targetRate');
      const min = Math.max(0, (row.segment_conversion_rate || 0) * 100);
      const max = Math.min(95, Math.max((row.benchmark_conversion_rate || 0) * 100 + 8, min + 2));
      slider.min = min.toFixed(1);
      slider.max = max.toFixed(1);
      if (!slider.value || Number(slider.value) < min || Number(slider.value) > max) {{
        slider.value = ((row.benchmark_conversion_rate || row.segment_conversion_rate || 0) * 100).toFixed(1);
      }}
      renderScenario();
    }}

    function renderScenario() {{
      const row = selectedRow();
      const target = Number(document.getElementById('targetRate').value) / 100;
      const gap = Math.max(0, target - (row.segment_conversion_rate || 0));
      const missed = (row.begin_checkout_sessions || 0) * gap;
      const revenue = missed * (row.average_order_value || 0);
      document.getElementById('targetRateLabel').textContent = `${{pct(target)}} target`;
      document.getElementById('scenarioDetails').innerHTML = [
        metricBox('Scenario missed conversions', fmtOne.format(missed), 'derived from selected target rate'),
        metricBox('Scenario revenue opportunity', money(revenue), 'derived from selected target rate')
      ].join('');
    }}

    function renderOpportunityTable() {{
      const rows = currentFilteredOpportunities().slice(0, 12);
      document.getElementById('opportunityTable').innerHTML = rows.map(row => `
        <tr>
          <td>${{row.segment_name}}</td>
          <td>${{pct(row.segment_conversion_rate)}}</td>
          <td>${{pct(row.benchmark_conversion_rate)}}</td>
          <td>${{pct(row.conversion_rate_gap)}}</td>
          <td>${{fmtOne.format(row.estimated_missed_conversions || 0)}}</td>
          <td>${{money(row.estimated_revenue_opportunity)}}</td>
        </tr>
      `).join('');
    }}

    function renderExperiment() {{
      const exp = packet.experiment_feasibility;
      document.getElementById('experimentDetails').innerHTML = [
        metricBox('Baseline CVR', pct(exp.baseline_conversion_rate), 'baseline_conversion_rate'),
        metricBox('MDE relative lift', pct(exp.mde_relative_lift), 'mde_relative_lift'),
        metricBox('Sample per variant', num(exp.required_sample_per_variant), 'required_sample_per_variant'),
        metricBox('Estimated duration', `${{num(exp.estimated_test_duration_days)}} days`, 'estimated_test_duration_days')
      ].join('');
      document.getElementById('experimentNarrative').textContent = exp.feasibility_interpretation;
      document.getElementById('experimentNextStep').textContent = exp.recommended_next_step;
    }}

    function bindControls() {{
      ['segmentSearch', 'deviceFilter', 'sortMode'].forEach(id => {{
        document.getElementById(id).addEventListener('input', renderOpportunityList);
      }});
      document.getElementById('targetRate').addEventListener('input', renderScenario);
      document.getElementById('evidenceToggle').addEventListener('change', (event) => {{
        document.body.classList.toggle('show-evidence', event.target.checked);
      }});
    }}

    renderKpis();
    renderFunnel();
    renderDeviceOptions();
    bindControls();
    renderOpportunityList();
    renderExperiment();
  </script>
</body>
</html>
"""


def build_dashboard(
    packet_path: str | Path = "outputs/metric_evidence_packet.json",
    opportunity_inputs_path: str | Path = "data/opportunity_inputs.csv",
    output_path: str | Path = "dashboard/index.html",
) -> None:
    packet = load_json(packet_path)
    opportunities = normalize_opportunity_rows(load_csv(opportunity_inputs_path))
    payload = {
        "packet": packet,
        "opportunities": opportunities,
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html_template(payload), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a self-contained HTML dashboard.")
    parser.add_argument("--packet", default="outputs/metric_evidence_packet.json")
    parser.add_argument("--opportunity-inputs", default="data/opportunity_inputs.csv")
    parser.add_argument("--output", default="dashboard/index.html")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_dashboard(
        packet_path=args.packet,
        opportunity_inputs_path=args.opportunity_inputs,
        output_path=args.output,
    )
