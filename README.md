# Dash Genie

A Plotly Dash sales dashboard template demonstrating core Dash patterns — Mantine UI components, AG Grid data table, Plotly charting, and reactive callbacks.

---

## Tech Stack

- [Dash 4](https://dash.plotly.com/) — Python web framework for data apps
- [Dash Mantine Components 2.6](https://www.dash-mantine-components.com/) — Mantine UI for Dash (layout, cards, buttons)
- [dash-ag-grid](https://dash.plotly.com/dash-ag-grid) — AG Grid data table with sort, filter, pagination
- [Plotly](https://plotly.com/python/) — Interactive charts

---

## Features

- **KPI cards** — total revenue, units sold, avg growth (color-coded)
- **Bar chart** — revenue aggregated by product
- **AG Grid table** — sortable, filterable, paginated detail table with conditional cell styling
- **Refresh button** — single callback regenerates all data and updates every component

---

## Quickstart

```bash
# 1. Clone
git clone <repo-url>
cd Dash-genie

# 2. Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
```

Open [http://localhost:8050](http://localhost:8050) in your browser.

> **GitHub Codespaces:** The port is auto-forwarded. Set port `8050` to **Public** in the Ports tab to share the preview URL.

---

## Project Structure

```
Dash-genie/
├── app.py              # Main Dash app — layout, constants, callback
├── requirements.txt    # Python dependencies
├── CLAUDE.md           # Claude Code context (architecture, conventions)
└── .gitignore
```

---

## How It Works

### Layout
`app.py` uses a single `dmc.MantineProvider` → `dmc.AppShell` structure:
- **Header** — app name and subtitle
- **Main** — stacked: page title + refresh button, KPI cards, chart, table

### Callback
One `@callback` handles everything triggered by the Refresh button:
```
Input:  refresh-btn (n_clicks)
Output: data-table (rowData)
        revenue-chart (figure)
        kpi-cards (children)
```
`prevent_initial_call=False` means it also runs on page load to populate the KPI cards and chart.

### Data
`generate_data()` produces 10 random rows with: `product`, `region`, `units_sold`, `revenue`, `growth`. Replace this function with a real data source (database, API, CSV) to use as a real dashboard.

---

## Extending

| Goal | What to do |
|---|---|
| Add a new chart | Add a `dcc.Graph` in layout, add an `Output` to the callback |
| Connect real data | Replace `generate_data()` with a data service; add `dcc.Store` for caching |
| Multi-page app | Add `dash.page_registry`, split layout into `pages/` |
| Dark mode | Change `colorScheme` in `dmc.MantineProvider` theme, add a toggle button |
| Tests | Add `tests/test_data.py`, test output shape of `generate_data()` |
