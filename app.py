"""
Dash Genie — Sales Dashboard

Demonstrates core Dash patterns:
  - Dash Mantine Components (DMC) for layout and UI
  - dash-ag-grid for sortable/filterable/paginated data table
  - Plotly for bar chart visualization
  - Single callback driving multiple outputs from one button click

See CLAUDE.md for architecture decisions and conventions.
"""

import random

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc

# ------------------------------------------------------------------
# Domain constants
# ------------------------------------------------------------------
PRODUCTS = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Doohickey Z"]
REGIONS = ["North", "South", "East", "West"]

# Data generation tuning
DATA_ROW_COUNT = 10
UNITS_MIN, UNITS_MAX = 50, 500
REVENUE_MIN, REVENUE_MAX = 1_000.0, 20_000.0
GROWTH_MIN, GROWTH_MAX = -15.0, 40.0

# Color palette — never hardcode hex values inline
CHART_BLUE = "#339af0"
GROWTH_POSITIVE_COLOR = "#2f9e44"
GROWTH_NEGATIVE_COLOR = "#e03131"
GRID_COLOR = "#f1f3f5"


# ------------------------------------------------------------------
# Sample data
# ------------------------------------------------------------------
def generate_data() -> list[dict]:
    """Generate a list of random sales row dicts.

    Returns DATA_ROW_COUNT rows, each with: id, product, region,
    units_sold, revenue, growth.
    """
    return [
        {
            "id": i + 1,
            "product": random.choice(PRODUCTS),
            "region": random.choice(REGIONS),
            "units_sold": random.randint(UNITS_MIN, UNITS_MAX),
            "revenue": round(random.uniform(REVENUE_MIN, REVENUE_MAX), 2),
            "growth": round(random.uniform(GROWTH_MIN, GROWTH_MAX), 1),
        }
        for i in range(DATA_ROW_COUNT)
    ]


# ------------------------------------------------------------------
# AG Grid column definitions
# ------------------------------------------------------------------
COLUMN_DEFS = [
    {"field": "id", "headerName": "#", "width": 60},
    {"field": "product", "headerName": "Product", "flex": 1},
    {"field": "region", "headerName": "Region", "flex": 1},
    {
        "field": "units_sold",
        "headerName": "Units Sold",
        "flex": 1,
        "type": "numericColumn",
    },
    {
        "field": "revenue",
        "headerName": "Revenue ($)",
        "flex": 1,
        "type": "numericColumn",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
    },
    {
        "field": "growth",
        "headerName": "Growth (%)",
        "flex": 1,
        "type": "numericColumn",
        "cellStyle": {
            "function": (
                f"params.value >= 0 "
                f"? {{'color': '{GROWTH_POSITIVE_COLOR}'}} "
                f": {{'color': '{GROWTH_NEGATIVE_COLOR}'}}"
            )
        },
    },
]


# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dash Genie"

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=dmc.AppShell(
        header={"height": 60},
        padding="md",
        children=[
            dmc.AppShellHeader(
                dmc.Group(
                    children=[
                        dmc.Text("Dash Genie", fw=700, size="xl", c="blue"),
                        dmc.Text("Sales Dashboard", size="sm", c="dimmed"),
                    ],
                    h="100%",
                    px="md",
                    gap="xs",
                )
            ),
            dmc.AppShellMain(
                dmc.Stack(
                    gap="lg",
                    children=[
                        # Page title + refresh button
                        dmc.Group(
                            children=[
                                dmc.Title("Sales Overview", order=2),
                                dmc.Button(
                                    "Refresh Data",
                                    id="refresh-btn",
                                    variant="filled",
                                    color="blue",
                                    leftSection=dmc.Text("↻", size="lg"),
                                ),
                            ],
                            justify="space-between",
                        ),
                        # KPI summary cards
                        dmc.SimpleGrid(
                            id="kpi-cards",
                            cols={"base": 1, "sm": 3},
                            children=[],
                        ),
                        # Bar chart
                        dmc.Paper(
                            shadow="sm",
                            p="md",
                            radius="md",
                            withBorder=True,
                            children=[
                                dmc.Text("Revenue by Product", fw=600, size="md", mb="sm"),
                                dcc.Loading(
                                    color=CHART_BLUE,
                                    children=dcc.Graph(
                                        id="revenue-chart",
                                        style={"height": "320px"},
                                    ),
                                ),
                            ],
                        ),
                        # Detail table
                        dmc.Paper(
                            shadow="sm",
                            p="md",
                            radius="md",
                            withBorder=True,
                            children=[
                                dmc.Text("Detail Table", fw=600, size="md", mb="sm"),
                                dcc.Loading(
                                    color=CHART_BLUE,
                                    children=dag.AgGrid(
                                        id="data-table",
                                        columnDefs=COLUMN_DEFS,
                                        rowData=[],
                                        defaultColDef={
                                            "sortable": True,
                                            "filter": True,
                                            "resizable": True,
                                        },
                                        dashGridOptions={
                                            "pagination": True,
                                            "paginationPageSize": 10,
                                        },
                                        style={"height": "340px"},
                                        className="ag-theme-alpine",
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
            ),
        ],
    ),
)


# ------------------------------------------------------------------
# Callback: refresh button regenerates all outputs
# ------------------------------------------------------------------
@callback(
    Output("data-table", "rowData"),
    Output("revenue-chart", "figure"),
    Output("kpi-cards", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=False,
)
def refresh_data(n_clicks: int | None) -> tuple[list[dict], go.Figure, list]:
    """Regenerate sample data and update table, chart, and KPI cards.

    Runs on page load (prevent_initial_call=False) and on every
    Refresh button click. Returns safe empty fallbacks on error.
    """
    try:
        rows = generate_data()

        # ---- KPI cards ----
        total_revenue = sum(r["revenue"] for r in rows)
        total_units = sum(r["units_sold"] for r in rows)
        avg_growth = round(sum(r["growth"] for r in rows) / len(rows), 1)

        kpi_data = [
            ("Total Revenue", f"${total_revenue:,.0f}", "green"),
            ("Total Units Sold", f"{total_units:,}", "blue"),
            ("Avg Growth", f"{avg_growth}%", "orange" if avg_growth >= 0 else "red"),
        ]
        cards = [
            dmc.Card(
                withBorder=True,
                shadow="sm",
                radius="md",
                p="md",
                children=[
                    dmc.Text(label, size="xs", c="dimmed", tt="uppercase", fw=600),
                    dmc.Text(value, size="xl", fw=700, c=color),
                ],
            )
            for label, value, color in kpi_data
        ]

        # ---- Bar chart — aggregate revenue per product ----
        product_rev: dict[str, float] = {}
        for r in rows:
            product_rev[r["product"]] = product_rev.get(r["product"], 0) + r["revenue"]

        fig = go.Figure(
            go.Bar(
                x=list(product_rev.keys()),
                y=list(product_rev.values()),
                marker_color=CHART_BLUE,
                text=[f"${v:,.0f}" for v in product_rev.values()],
                textposition="outside",
            )
        )
        fig.update_layout(
            margin=dict(t=20, b=40, l=40, r=20),
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(title="Revenue ($)", gridcolor=GRID_COLOR, tickformat="$,.0f"),
            xaxis=dict(title="Product"),
            font=dict(family="sans-serif", size=12),
        )

        return rows, fig, cards

    except Exception:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            annotations=[
                dict(text="Error loading data", x=0.5, y=0.5, showarrow=False)
            ],
        )
        return [], empty_fig, []


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
