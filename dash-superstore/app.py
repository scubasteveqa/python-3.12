import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly

df = pd.read_excel(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-28/Sample%20-%20Superstore.xls"
)
df = df[df["Country/Region"] == "United States"]
df["Category"] = pd.Categorical(df["Category"], categories=df["Category"].unique())
df["gm"] = df["Profit"] / df["Sales"] * 100
df["Order Date"] = df["Order Date"].dt.strftime("%Y-%m-%d")
df["Ship Date"] = df["Ship Date"].dt.strftime("%Y-%m-%d")
df["Year"] = df["Ship Date"].str[:4]
df.sort_values("State/Province", inplace=True)
ALL_STATES = df["State/Province"].unique().tolist()

# Range for the colorscales
MIN_GM = -150.0
MAX_GM = 150.0

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


def create_bar(dff, first_card=True):
    # Group by category and calculate total sales and total profit
    grouped_df = (
        dff.groupby(["Category"], observed=False)
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
    )

    # Calculate GM%
    grouped_df["gm%"] = (grouped_df["Profit"] / grouped_df["Sales"]) * 100
    # Format label
    grouped_df["GM%"] = grouped_df["gm%"].apply(
        lambda x: f"{x:.1f}%" if isinstance(x, float) else "N/A"
    )

    # Create a horizontal bar chart
    fig = px.bar(
        grouped_df,
        x="gm%",
        y="Category",
        color="gm%",
        color_continuous_scale="rdbu",
        range_color=[MIN_GM, MAX_GM],
        orientation="h",
        text="GM%",
        template="simple_white",
        hover_data={"gm%": False},
        height=175 if first_card else 100,
    )
    fig.add_vline(
        x=0,
        line_width=3,
    )
    fig.update_layout(xaxis_range=[-75, 75], margin=dict(l=5, r=5, t=0, b=0))
    if not first_card:
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
    return fig


def get_color(gm):
    """
    returns the color for the gm%  based on the same colorscale as the bar charts
    """

    # Clamp the gm value between MIN_GM and MAX_GM
    gm = max(MIN_GM, min(gm, MAX_GM))

    normalized_gm = (gm - MIN_GM) / (MAX_GM - MIN_GM)

    color = plotly.colors.sample_colorscale(
        plotly.colors.sequential.RdBu,
        samplepoints=normalized_gm,
    )
    return color[0]


state_dropdown = html.Div(
    [
        dbc.Label("Select a State", html_for="state_dropdown"),
        dcc.Dropdown(id="state-dropdown", value=[], multi=True),
    ],
    className="my-4",
)

region_dropdown = html.Div(
    [
        dbc.Label("Select a Region", html_for="region_dropdown"),
        dcc.Dropdown(
            id="region-dropdown",
            options=df["Region"].unique(),
            value=["South"],
            multi=True,
        ),
    ],
    className="mb-4",
)

date_checklist = html.Div(
    [
        dbc.Label("Select Dates"),
        dbc.Checklist(
            options=["2024", "2023", "2022", "2021"],
            value=["2024", "2023", "2022", "2021"],
            id="date-checklist",
        ),
    ]
)

control_panel = dbc.Card(
    dbc.CardBody(
        [region_dropdown, state_dropdown, date_checklist],
        className="bg-light",
    )
)


heading = html.H4(
    "Superstore Gross Margin Analysis by Region",
    className="bg-secondary text-white p-2 mb-4",
)


def make_grid():
    df["gm_color"] = df["gm"].apply(lambda x: get_color(x))
    other_grid_columns = [
        "Sub-Category", "Order ID",  "Ship Date", "Ship Mode", "Customer ID", "Segment", "City",
        "Postal Code", "Product ID", "Product Name", "Quantity",  "Discount",
    ]

    grid = dag.AgGrid(
        id="grid",
        rowData=df.to_dict("records"),
        columnDefs=[{"field": f} for f in ["Region", "State/Province", "Category"]]
        + [
            {
                "field": "Sales",
                "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
                "type": "rightAligned",
            },
            {
                "field": "Profit",
                "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
                "type": "rightAligned",
            },
            {
                "field": "gm",
                "valueFormatter": {"function": "d3.format(',.1f')(params.value) + '%'"},
                "cellStyle": {
                    "function": "params.value && {'backgroundColor': params.data.gm_color}",
                },
                "type": "rightAligned",
            },
        ]
        + [{"field": f} for f in other_grid_columns],
        defaultColDef={"filter": True, "floatingFilter": True},
        columnSize='autoSize',
        dashGridOptions={"suppressColumnVirtualisation": True}
    )
    return grid


app.layout = dbc.Container(
    [
        heading,
        dbc.Row(
            [
                dbc.Col(control_panel, md=3),
                dbc.Col([html.Div(id="panel"), make_grid()], md=9),
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("state-dropdown", "options"),
    Output("state-dropdown", "value"),
    Input("region-dropdown", "value"),
)
def update_state_options(region):
    if not region:
        return ALL_STATES, []
    dff = df[df["Region"].isin(region)]
    return dff["State/Province"].unique().tolist(), []


@app.callback(
    Output("panel", "children"),
    Output("grid", "dashGridOptions"),
    Input("state-dropdown", "value"),
    Input("region-dropdown", "value"),
    Input("date-checklist", "value"),
)
def update(states, regions, years):
    dff = df[df["Year"].isin(years)]
    if not states and not regions:
        states = ALL_STATES
    if not states and regions:
        dff = dff[dff["Region"].isin(regions)]
        states = dff["State/Province"].unique().tolist()

    # filter grid
    my_filter = f"{states}.includes(params.data['State/Province']) && {years}.includes(params.data['Year'])"
    grid_options = {
        "isExternalFilterPresent": {"function": "true"},
        "doesExternalFilterPass": {"function": my_filter},
    }

    # make summary card
    dff = dff[dff["State/Province"].isin(states)]
    state_gm = 0
    if dff["Sales"].sum() != 0:
        state_gm = dff["Profit"].sum() / dff["Sales"].sum() * 100

    fig = create_bar(dff)
    first_card = dbc.Card(
        [
            dbc.CardHeader(
                f"Total Selected {state_gm:.1f}%",
                style={"backgroundColor": get_color(state_gm)},
            ),
            dcc.Graph(
                figure=fig,
                id="total",
                config={"displayModeBar": False},
                className="p-1",
            ),
        ],
        style={"maxWidth": 800},
        className="mb-4",
    )

    # make panel with cards by state
    state_panel = []
    for i in states:
        dff_state = dff[dff["State/Province"] == i]
        state_gm = 0
        if dff_state["Sales"].sum() != 0:
            state_gm = dff_state["Profit"].sum() / dff_state["Sales"].sum() * 100

        fig = create_bar(dff_state, first_card=False)
        card = dbc.Card(
            [
                dbc.CardHeader(
                    f"{i} {state_gm:.1f}%",
                    style={"backgroundColor": get_color(state_gm)},
                ),
                dcc.Graph(
                    figure=fig, id=i, config={"displayModeBar": False}, className="p-1"
                ),
            ],
            style={"width": 200},
            className="mb-2",
        )
        state_panel.append(dbc.Col(card))

    return [
        dbc.Row(dbc.Col(first_card)),
        dbc.Row(state_panel, className="g-1"),
    ], grid_options


if __name__ == "__main__":
    app.run(debug=True)
