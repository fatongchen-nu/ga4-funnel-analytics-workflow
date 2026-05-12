# HTML Dashboard

Generate a self-contained interactive dashboard:

```bash
python src/build_metric_evidence_packet.py
python src/build_tableau_exports.py
python src/build_html_dashboard.py
```

Open:

```text
dashboard/index.html
```

The dashboard embeds the current metric evidence packet and opportunity table, so it can be opened directly in a browser without a server, external JavaScript, or live API calls.

## Included Interactions

- Segment search
- Device filter
- Opportunity sort controls
- Clickable segment detail panel
- Target conversion scenario slider
- Evidence path toggle
- Responsive funnel and opportunity views

## Evidence Rule

All displayed metrics come from:

```text
outputs/metric_evidence_packet.json
data/opportunity_inputs.csv
```
