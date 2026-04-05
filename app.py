import random
import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc

# ------------------------------------------------------------------
# Sample data helpers
# ------------------------------------------------------------------
PRODUCTS = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Doohickey Z"]
REGIONS = ["North", "South", "East", "West"]


def generate_data():
    rows = []
    for i in range(10):
        rows.append(
            {
                "id": i + 1,
                "product": random.choice(PRODUCTS),
                "region": random.choice(REGIONS),
                "units_sold": random.randint(50, 500),
                "revenue": round(random.uniform(1000, 20000), 2),
                "growth": round(random.uniform(-15, 40), 1),
            }
        )
    return rows


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
            "function": "params.value >= 0 ? {'color': '#2f9e44'} : {'color': '#e03131'}"
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
                        # Header row
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
                        # KPI cards
                        dmc.SimpleGrid(
                            id="kpi-cards",
                            cols={"base": 1, "sm": 3},
                            children=[],
                        ),
                        # Chart
                        dmc.Paper(
                            shadow="sm",
                            p="md",
                            radius="md",
                            withBorder=True,
                            children=[
                                dmc.Text(
                                    "Revenue by Product",
                                    fw=600,
                                    size="md",
                                    mb="sm",
                                ),
                                dcc.Graph(id="revenue-chart", style={"height": "320px"}),
                            ],
                        ),
                        # Table
                        dmc.Paper(
                            shadow="sm",
                            p="md",
                            radius="md",
                            withBorder=True,
                            children=[
                                dmc.Text(
                                    "Detail Table",
                                    fw=600,
                                    size="md",
                                    mb="sm",
                                ),
                                dag.AgGrid(
                                    id="data-table",
                                    columnDefs=COLUMN_DEFS,
                                    rowData=generate_data(),
                                    defaultColDef={
                                        "sortable": True,
                                        "filter": True,
                                        "resizable": True,
                                    },
                                    dashGridOptions={"pagination": True, "paginationPageSize": 10},
                                    style={"height": "340px"},
                                    className="ag-theme-alpine",
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
# Callback: refresh button regenerates all data
# ------------------------------------------------------------------
@callback(
    Output("data-table", "rowData"),
    Output("revenue-chart", "figure"),
    Output("kpi-cards", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=False,
)
def refresh_data(n_clicks):
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

    # ---- Chart ----
    # Aggregate revenue per product
    product_rev: dict[str, float] = {}
    for r in rows:
        product_rev[r["product"]] = product_rev.get(r["product"], 0) + r["revenue"]

    products = list(product_rev.keys())
    revenues = list(product_rev.values())

    fig = go.Figure(
        go.Bar(
            x=products,
            y=revenues,
            marker_color="#339af0",
            text=[f"${v:,.0f}" for v in revenues],
            textposition="outside",
        )
    )
    fig.update_layout(
        margin=dict(t=20, b=40, l=40, r=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(
            title="Revenue ($)",
            gridcolor="#f1f3f5",
            tickformat="$,.0f",
        ),
        xaxis=dict(title="Product"),
        font=dict(family="sans-serif", size=12),
    )

    return rows, fig, cards


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
