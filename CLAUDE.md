# Dash Genie — Claude Context

Read this file at the start of every session. It gives full project context so exploration is not needed.

---

## Project Overview

**Dash Genie** is a Plotly Dash sales dashboard demonstrating core Dash patterns with Dash Mantine Components (DMC) for UI, dash-ag-grid for tabular data, and Plotly for charting.

This is a learning/template project — the goal is clean, idiomatic Dash code that can be used as a reference for building real dashboards.

---

## Stack

| Library | Version | Role |
|---|---|---|
| `dash` | >=4.0.0 | Core framework, callbacks, routing |
| `dash-mantine-components` | >=2.6.0 | UI components (layout, cards, buttons) |
| `dash-ag-grid` | >=31.0.0 | Data table (sort, filter, paginate) |
| `plotly` | >=5.0.0 | Bar chart and future visualizations |

**Python:** 3.10+ (uses `X | Y` union type hints)

---

## File Map

```
app.py              — Single-file Dash app (layout + callbacks)
requirements.txt    — Python dependencies
CLAUDE.md           — This file (Claude context)
README.md           — Human-facing docs
.gitignore          — Excludes __pycache__, .venv, .env, build/
```

---

## Architecture Decisions

- **Single file (`app.py`):** App is small enough that splitting into pages/components would add complexity without benefit. When it grows beyond ~300 lines or adds multi-page routing, split into `layout.py`, `callbacks.py`, `components/`.
- **dash-ag-grid over dmc.Table:** AG Grid provides built-in sort, filter, and pagination with zero extra callback code. DMC's `Table` is for static/simple display only.
- **Single callback for all outputs:** `refresh_data()` drives the table, chart, and KPI cards from one button click. This avoids redundant data generation and keeps the data consistent across all three outputs.
- **`prevent_initial_call=False`:** The callback runs on page load to populate KPI cards and chart (which start empty in layout). This is intentional.
- **No `dcc.Store`:** Data is regenerated fresh each callback rather than cached. Fine for sample data; real data sources should use `dcc.Store` for caching.

---

## Dev Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run app (hot-reload enabled)
python app.py
# → http://localhost:8050

# Quick import check (no server start)
python -c "import app; print('OK')"
```

---

## Code Conventions

### Constants (top of file, after imports)
```python
PRODUCTS = [...]          # Domain list constants — ALL_CAPS
REGIONS = [...]
DATA_ROW_COUNT = 10       # Numeric tuning constants
CHART_BLUE = "#339af0"    # Color palette — never hardcode hex inline
GROWTH_POSITIVE_COLOR = "#2f9e44"
GROWTH_NEGATIVE_COLOR = "#e03131"
COLUMN_DEFS = [...]       # AG Grid column config
```

### Callbacks
- Use `@callback` (not `@app.callback`) — the module-level decorator
- Always wrap callback body in `try/except` — return safe fallback on error
- Name callbacks as verbs: `refresh_data`, `update_chart`, `filter_table`
- Each callback owns one logical action; don't chain side effects

### Components
- All layout lives in `app.layout` — no layout helper functions unless reused 3+ times
- Use `dmc.Paper` with `withBorder=True, shadow="sm", radius="md"` as the standard card wrapper
- Wrap async outputs in `dcc.Loading` for UX feedback

### Type hints
- All functions must have return type annotations
- Use `list[dict]` not `List[Dict]` (Python 3.10+ style)

---

## Known Issues / TODO

- [ ] Sample data is purely random — no seed, not reproducible for testing
- [ ] No unit tests — add `tests/test_data.py` to test `generate_data()` output shape
- [ ] Chart only shows bar — consider adding a line chart toggle (units_sold over time)
- [ ] No dark mode toggle — DMC supports `colorScheme: "dark"` in MantineProvider
- [ ] `dcc.Loading` color should match Mantine theme blue (`#339af0`)
- [ ] For real data: replace `generate_data()` with a data service layer and use `dcc.Store`
