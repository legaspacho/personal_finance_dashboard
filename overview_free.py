# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 17:28:20 2021

@author: LHERMITTE_G
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash
from main_pandas_exceptions import main
from dash.dash_table import DataTable
from scipy.optimize import root
import numpy as np
import math
import os
from pathlib import Path

cwd = os.getcwd()
path = Path(cwd) / "datasets"
main(cwd)

# Load CSVs once at startup
_df_category_raw = pd.read_csv(path / "spent_category.csv")
_df_category_raw.loc[:, "day"] = 1
_df_category_raw["Date"] = pd.to_datetime(_df_category_raw[["year", "month", "day"]])

_df_all_raw = pd.read_csv(path / "spent_all.csv")
_df_all_raw["Date"] = pd.to_datetime(_df_all_raw[["year", "month", "day"]])

# create_dashboard()
app = dash.Dash(__name__, prevent_initial_callbacks=False, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def apply_dark_theme(fig, **kwargs):
    default_legend = dict(
        x=0.05, y=1, xanchor="left", yanchor="top",
        bgcolor='rgba(255, 255, 255, 0.2)',
        bordercolor='white', borderwidth=1,
        font=dict(color='white')
    )
    if 'legend' in kwargs:
        default_legend.update(kwargs.pop('legend'))
    fig.update_layout(
        paper_bgcolor='#333333',
        plot_bgcolor='#333333',
        font=dict(color='white', family="Arial, sans-serif", size=12),
        hoverlabel=dict(font_size=14, font_color='white'),
        title_font_size=14,
        legend=default_legend,
        **kwargs
    )
    return fig

def kpi_color(current, comparison, higher_is_better=True):
    """Return green if improving, red if worsening, white if equal."""
    if higher_is_better:
        return '#00CC66' if current > comparison else '#FF4444' if current < comparison else 'white'
    return '#00CC66' if current < comparison else '#FF4444' if current > comparison else 'white'

list_columns=["year","month","category","fix_variable","Description","Amount"]
list_columns_type = [
    {"id": "year", "name": "year", "type": "numeric"},
    {"id": "month", "name": "month", "type": "numeric"},
    {"id": "category", "name": "category", "type": "text"},
    {"id": "fix_variable", "name": "fix_variable", "type": "text"},
    {"id": "Description", "name": "Description", "type": "text"},
    {"id": "Amount", "name": "Amount", "type": "numeric"},
]
categories_include = ["all","taxes","investment","holidays","housing","restaurant","insurance","transportation","sport","others","food","entertainment","clothes","health"]

def generate_months():
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Define the range of months from October 2021 to December 2024
    start_year = 2021
    start_month = 9
    end_year = current_date.year + 1
    end_month = 12

    months = {}
    index = 9  # Start index for October 2021
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == start_year and month < start_month:
                continue
            if year == end_year and month > end_month:
                continue
            months[index] = f"{year}-{month:02d}"
            index += 1

    # Set max value based on the current month/year
    max_value = (current_year - start_year) * 12 + (current_month) + 1
    return months, max_value, start_month

# Get month labels and maximum value
months, max_value, start_month = generate_months()

# Sorting operators (https://dash.plotly.com/datatable/filtering)

app.layout = html.Div(
    children=[
        html.Div(id="app_init"),
        
        # Dark background for the entire app
        html.Div(style={'backgroundColor': '#1a1a1a', 'padding': '20px'}, children=[
            # First row with controls
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Select categories to include:", className="text-white"),
                                    dcc.Checklist(
                                        id="include_category",
                                        value=["all"],
                                        options=[{"label": i, "value": i} for i in categories_include],
                                        inline=True,
                                        className="text-white",
                                        inputStyle={"marginRight": "4px"},
                                        labelStyle={"color": "white", "marginRight": "8px"},
                                    ),
                                ]
                            ),
                            className="h-100",  # Make card take full height
                            style={'fontSize': '12px', 'backgroundColor': '#333333'},
                        ),
                        width=2,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Select Aggregation method:", className="text-white"),
                                    dcc.RadioItems(
                                        id="spent_aggregation",
                                        value="all",
                                        labelStyle={'display': 'block', 'color': 'white'},
                                        options=[
                                            {"label": "All time", "value": "all"},
                                            {"label": "Yearly avg", "value": "yearly"},
                                            {"label": "Monthly avg", "value": "monthly"},
                                        ],
                                        className="text-white",
                                    ),
                                ]
                            ),
                            className="h-100",  # Make card take full height
                            style={'fontSize': '12px', 'backgroundColor': '#333333'},
                        ),
                        width=1,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Stock details:", className="text-white"),
                                    dcc.RadioItems(
                                        id="stock_details",
                                        value="highlevel",
                                        labelStyle={'display': 'block', 'color': 'white'},
                                        options=[
                                            {"label": "High level", "value": "highlevel"},
                                            {"label": "Details Dividends", "value": "details_dividends"},
                                            {"label": "Details Stocks", "value": "details_stocks"},
                                            {"label": "Deep Finder YTD", "value": 'deepfinder_ytd'},
                                            {"label": "Deep Finder inception", "value": 'deepfinder_inception'},
                                        ],
                                        className="text-white",
                                    ),
                                ]
                            ),
                            className="h-100",  # Make card take full height
                            style={'fontSize': '12px', 'backgroundColor': '#333333'},
                        ),
                        width=2,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Aggregate per category?:", className="text-white"),
                                    dcc.RadioItems(
                                        id="aggregate_category",
                                        value="yes",
                                        labelStyle={'display': 'block', 'color': 'white'},
                                        options=[
                                            {"label": "yes", "value": "yes"},
                                            {"label": "no", "value": "no"},
                                        ],
                                        className="text-white",
                                    ),
                                ]
                            ),
                            className="h-100",  # Make card take full height
                            style={'fontSize': '12px', 'backgroundColor': '#333333'},
                        ),
                        width=1,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Select Date from/to:", className="text-white"),
                                    dcc.RangeSlider(
                                        id='month_slider',
                                        min=start_month,
                                        max=max_value,
                                        value=[start_month, max_value],
                                        marks={
                                            i: {
                                                'label': month,
                                                'style': {
                                                    'color': 'white',
                                                    'transform': 'rotate(45deg)',
                                                    'whiteSpace': 'nowrap',
                                                    'marginLeft': '0px',
                                                    'position': 'absolute',
                                                    'left': f'{(i - 10) / (max_value - 10) * 100}%',
                                                    'transformOrigin': 'left bottom',
                                                }
                                            } for i, month in months.items() if i % 2 == 0
                                        },
                                        step=1,
                                        included=True,
                                    ),
                                ]
                            ),
                            className="h-100",  # Make card take full height
                            style={'fontSize': '12px', 'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-4",  # Add margin-bottom to separate the row
            ),

            # KPI Row 1
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Income saved YTD (saving rate)", className="text-white"),
                                    html.Div(id='saved_ytd_value', className='card-text text-white'),  # Placeholder for value
                                    html.Div(id='saved_ytd_sub', className='card-subtext text-white'),  # Placeholder for sub
                                ]
                            ),
                            style={'backgroundColor': '#333333'},
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Restaurant YTD", className="text-white"),
                                    html.Div(id='restaurant_YTD_value', className='card-text text-white'),  # Placeholder for value
                                    html.Div(id='restaurant_YTD_sub', className='card-subtext text-white'),  # Placeholder for sub
                                ]
                            ),
                            style={'backgroundColor': '#333333'},
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Restaurant current month", className="text-white"),
                                    html.Div(id='restaurant_month_value', className='card-text text-white'),  # Placeholder for value
                                    html.Div(id='restaurant_month_sub', className='card-subtext text-white'),  # Placeholder for sub
                                ]
                            ),
                            style={'backgroundColor': '#333333'},
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Dividends YtD (equity YtD)", className="text-white"),
                                    html.Div(id='dividends_YtD_value', className='card-text text-white'),
                                    html.Div(id='dividends_YtD_sub', className='card-subtext text-white'),
                                    html.Div(id='xirr_value', className='card-subtext text-white'),
                                ]
                            ),
                            style={'backgroundColor': '#333333'},
                        ),
                        width=3,
                    ),
                ],
                className="mb-4",
            ),

            # Row with Graphs
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Monthly spent (excl. investments)", className="card-title text-white"),
                                dcc.Graph(id="cumulative"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("IB DEGIRO", className="card-title text-white"),
                                dcc.Graph(id="stock_market_macro"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-4",
            ),

            # Another row with graphs
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("History spent breakdown", className="card-title text-white"),
                                dcc.Graph(id="max_overview"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("History spent breakdown", className="card-title text-white"),
                                dcc.Graph(id="treemap_graph"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-4",
            ),

            # Last row of graphs
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Monthly spent (excl. taxes, investments)", className="card-title text-white"),
                                dcc.Graph(id="line_graph"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Category over time", className="card-title text-white"),
                                dcc.Graph(id="category_time"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-4",
            ),

            # Year-over-year comparison
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader([
                                    "Year-over-Year comparison: ",
                                    dcc.Dropdown(
                                        id="yoy_category",
                                        options=[{"label": c, "value": c} for c in categories_include if c != "all"],
                                        value="restaurant",
                                        clearable=False,
                                        style={'width': '200px', 'display': 'inline-block', 'backgroundColor': '#444444', 'color': 'black'},
                                    ),
                                ], className="card-title text-white", style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                                dcc.Graph(id="yoy_graph"),
                            ],
                            style={'backgroundColor': '#333333'},
                        ),
                        width=12,
                    ),
                ],
                className="mb-4",
            ),

            # Individual transactions table
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Individual transactions", className="card-title text-white"),
                                    DataTable(
                                        id='new_built_table',
                                        columns=list_columns_type,
                                        data=[],  # Dynamically loading data here
                                        editable=False,
                                        filter_action='native',  # Enable column search functionality
                                        page_size=18,
                                        sort_action='native',  # Enable user to sort columns interactively
                                        style_header={  # Styling the header row
                                            'backgroundColor': '#444444',  # Dark gray header
                                            'color': 'white',  # White text in header
                                            'fontWeight': 'bold',  # Bold text for clarity
                                        },
                                        style_cell={  # Styling individual cells
                                            'backgroundColor': '#333333',  # Dark gray background
                                            'color': 'white',  # White text
                                            'border': '1px solid #444444',  # Light border for separation
                                            'textAlign': 'left',  # Align text to the left
                                        },
                                        style_table={  # Styling the overall table
                                            'height': 'auto',  # Adjust height to fit data
                                            'overflowY': 'auto',  # Scrollable table
                                        },
                                        style_data={  # Styling the data rows
                                            'backgroundColor': '#333333',  # Same dark background
                                            'color': 'white',  # White text for data
                                        },
                                        style_filter={
                                            'backgroundColor': '#444444',
                                            'color': 'white',
                                            'border': '1px solid #555555',
                                            'fontWeight': 'bold',
                                        },
                                        style_data_conditional=[  # Optional conditional formatting for hovering rows
                                            {
                                                'if': {'state': 'active'},  # Active (hovered) row
                                                'backgroundColor': '#555555',  # Darker gray on hover
                                                'border': '1px solid white',  # White border for hovered rows
                                            }
                                        ]
                                    ),
                                ]
                            ),
                            style={'backgroundColor': '#333333'},
                        ),
                        width=12,
                    ),
                ],
            ),
        ])
    ]
)


@app.callback(
    [
        Output("saved_ytd_value", "children"),
        Output("saved_ytd_sub", "children"),
        Output("restaurant_YTD_value", "children"),
        Output("restaurant_YTD_sub", "children"),
        Output("restaurant_month_value", "children"),
        Output("restaurant_month_sub", "children"),
    ],
    Input("app_init", "children"),

)
def update_kpis(children):

    df_finance_raw = _df_category_raw.copy()
    df_finance_raw_all = _df_all_raw.copy()

    #KPIS figures
    df_ytd = df_finance_raw_all[(df_finance_raw_all["category"] != "investment") & (df_finance_raw_all["category"] != "pillar2a") & (df_finance_raw_all["year"] == datetime.today().year)].copy()
    saved_ytd_raw = int(df_ytd["Amount"].sum().round())
    KPI_saved_value = f"{saved_ytd_raw:,} CHF"

    # Savings rate: saved / income
    income_ytd = df_finance_raw_all[(df_finance_raw_all["category"] == "salary") & (df_finance_raw_all["year"] == datetime.today().year)]["Amount"].sum()
    savings_rate = f" ({saved_ytd_raw / income_ytd * 100:.0f}% saved)" if income_ytd > 0 else ""
    KPI_saved_value = KPI_saved_value + savings_rate

    df_ytd_y1 = df_finance_raw_all[(df_finance_raw_all["category"] != "investment") & (df_finance_raw_all["category"] != "pillar2a") & (df_finance_raw_all["year"] == datetime.today().year -1)].copy()
    saved_y1_raw = int(df_ytd_y1["Amount"].sum().round())
    color_saved = kpi_color(saved_ytd_raw, saved_y1_raw, higher_is_better=True)
    df_KPI_saved_Y1 = html.Span(f"vs {saved_y1_raw:,} CHF last year", style={'color': color_saved})

    #KPI restaurant
    rest_ytd_raw = int(df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year)]["Amount"].sum().round())
    KPI_restaurant_value = f"{rest_ytd_raw:,} CHF"
    rest_y1_raw = int(df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year -1)]["Amount"].sum().round())
    color_rest = kpi_color(rest_ytd_raw, rest_y1_raw, higher_is_better=False)
    KPI_restaurant_value_Y1 = html.Span(f"vs {rest_y1_raw:,} CHF last year", style={'color': color_rest})

    #KPIs restaurant Monthly
    rest_m_raw = int(df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year) \
        & (df_finance_raw_all["month"] == datetime.today().month)]["Amount"].sum().round())
    KPI_restaurant_M_value = f"{rest_m_raw:,} CHF/m"
    prev_month = datetime.today().month - 1 if datetime.today().month > 1 else 12
    prev_month_year = datetime.today().year if datetime.today().month > 1 else datetime.today().year - 1
    rest_m1_raw = int(df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == prev_month_year) \
        & (df_finance_raw_all["month"] == prev_month)]["Amount"].sum().round())
    color_rest_m = kpi_color(rest_m_raw, rest_m1_raw, higher_is_better=False)
    KPI_restaurant_value_M1 = html.Span(f"vs {rest_m1_raw:,} CHF last month", style={'color': color_rest_m})

    return KPI_saved_value, df_KPI_saved_Y1, KPI_restaurant_value, KPI_restaurant_value_Y1, KPI_restaurant_M_value, KPI_restaurant_value_M1

@app.callback(
        Output("category_time", "figure"),
        Input("app_init", "children"),

)
def all_graphs( children):

    df_finance_raw = _df_category_raw.copy()

    df_category_sum = df_finance_raw
    df_category_sum = df_category_sum[~((df_category_sum["category"] == "taxes")
                              | (df_category_sum["category"] == "salary")
                              | (df_category_sum["category"] == "pillar2a")
                                | (df_category_sum["category"] == "investment"))].copy()
    df_category_sum = df_category_sum.groupby(["Date","category"],as_index=False)[["Amount"]].sum()
    df_category_sum = df_category_sum[~((df_category_sum["category"] == "others")&(df_category_sum["Amount"]>=8000))].copy()
    df_category_sum_pivot = pd.pivot(df_category_sum, index=['Date'], columns="category", values="Amount")
    df_category_sum_pivot.reset_index(inplace=True)  # drop frame pivot tables
    df_category_sum_pivot.fillna(0, inplace=True)
    df_category_sum_melt = df_category_sum_pivot.melt(id_vars=["Date"], var_name="category", value_name="Amount")
    df_category_sum = df_category_sum_melt
    df_category_sum['3m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=3).mean().reset_index(drop=True)
    df_category_sum['6m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=6).mean().reset_index(drop=True)
    df_category_sum['12m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=12).mean().reset_index(drop=True)
    df_category_sum['24m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=24).mean().reset_index(drop=True)

    unique_dates = df_category_sum['Date'].unique()
    # Find the maximum value in the 'date' column
    unique_dates_sorted = sorted(unique_dates, reverse=True)
    second_highest_unique_date = unique_dates_sorted[1]

    df_category_sum_latest = df_category_sum[df_category_sum["Date"] == second_highest_unique_date].copy()
    df_category_melt = df_category_sum_latest.melt(id_vars=["Date","category"], var_name="timeframe", value_name="value")

    df_category_melt = df_category_melt[~(df_category_melt["timeframe"] == "Amount")].copy()
    df_category_melt["value"] = df_category_melt["value"] * -1
    #df_category_melt = df_category_melt.sort_values(by=['value'], ascending=[False] )

    timeframe_order = ['3m_roll', '6m_roll', '12m_roll', '24m_roll']
    df_category_melt['timeframe'] = pd.Categorical(df_category_melt['timeframe'], categories=timeframe_order, ordered=True)

    df_3m_roll = df_category_melt[df_category_melt['timeframe'] == '3m_roll'].copy()
    sorted_categories = df_3m_roll.sort_values('value', ascending=False)['category'].tolist()

    df_category_melt['category'] = pd.Categorical(df_category_melt['category'], categories=sorted_categories, ordered=True)
    category_exclude = df_category_melt[(df_category_melt["timeframe"] == "3m_roll") & (df_category_melt["value"] < 0)]["category"].tolist()
    df_category_melt = df_category_melt[~(df_category_melt["category"].isin(category_exclude))]
    colors = ['black',"blue", 'green', 'red', 'orange', 'purple', 'brown']
    fig_category = go.Figure()

    i = 0
    for timeframe in df_category_melt["timeframe"].unique():
        df_category_melt_local = df_category_melt[df_category_melt["timeframe"] == timeframe].copy()
        # Sort df_category_melt_local to reflect the sorted order in categories
        df_category_melt_local = df_category_melt_local.sort_values(by='category', key=lambda x: x.map({cat: i for i, cat in enumerate(sorted_categories)}))
        
        fig_category.add_trace(go.Bar(
            name=timeframe,
            x=df_category_melt_local["category"],
            y=df_category_melt_local["value"],
            marker=dict(color=colors[i % len(colors)]),
        ))
        i += 1
    # Change the bar mode

    fig_category.update_layout(barmode='group')
    apply_dark_theme(fig_category,
        hovermode='x',
        xaxis=dict(title='Category', showgrid=True, gridcolor='lightgray', zeroline=False),
        yaxis=dict(title='Rolling Average CHF/month', showgrid=True, gridcolor='lightgray', zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig_category


@app.callback(
    [
        Output("max_overview", "figure"),
        Output("cumulative", "figure"),
        Output("treemap_graph", "figure"),
        Output("new_built_table", "data"),
    ],
    [
        Input(component_id="spent_aggregation", component_property="value"),
        Input(component_id="include_category", component_property="value"),
        Input(component_id="month_slider", component_property="value"),
    ]
)
def main_graphs( spent_aggregation, catgory_include, slider_date):

    start_date_str = months[slider_date[0]] + '-01'
    end_date_str = months[slider_date[1]] + '-01'

    df_finance_raw = _df_category_raw.copy()
    df_finance_raw_all = _df_all_raw.copy()

    df_finance = df_finance_raw[(df_finance_raw["Date"] >= start_date_str) & (df_finance_raw["Date"] <= end_date_str)].copy()
    df_finance_all = df_finance_raw_all[(df_finance_raw_all["Date"] >= start_date_str) & (df_finance_raw_all["Date"] <= end_date_str)].copy()

    if ("all" not in catgory_include) & (len(catgory_include)>0):
        df_finance = df_finance[df_finance["category"].isin(catgory_include)].copy()
        df_finance_all = df_finance_all[df_finance_all["category"].isin(catgory_include)].copy()

    #Filtering the datasets
    if spent_aggregation == "all":
        df_finance_max = df_finance.groupby(["category", "fix_variable"], as_index=False)[["Amount"]].sum()  # ,'category_name'
    elif spent_aggregation == "yearly":
        count_year = len(df_finance["year"].unique())
        df_finance_max = df_finance.groupby(["category", "fix_variable"], as_index=False)[["Amount"]].sum()  # ,'category_name'
        df_finance_max["Amount"] = df_finance_max["Amount"] / count_year
    elif spent_aggregation == "monthly":
        count_month = len(df_finance["Date"].unique())
        df_finance_max = df_finance.groupby(["category", "fix_variable"], as_index=False)[["Amount"]].sum()  # ,'category_name'
        df_finance_max["Amount"] = df_finance_max["Amount"] / count_month
        #df_finance_max = df_finance_max.groupby(["category"], as_index=False)[["Amount"]].mean()

    df_waterfall = df_finance_max.sort_values(by='Amount', key=abs, ascending=False)
    df_waterfall = df_waterfall[df_waterfall["category"] != "pillar2a"]
    df_waterfall = df_waterfall.groupby("category", as_index=False)[["Amount"]].sum()
    df_waterfall = df_waterfall.sort_values(by='Amount', key=abs, ascending=False)

    # #4 Transaction count per category on waterfall x-axis labels
    df_txn_count = df_finance_all.groupby("category", as_index=False).size().rename(columns={"size": "count"})
    count_map = dict(zip(df_txn_count["category"], df_txn_count["count"]))
    df_waterfall["label"] = df_waterfall["category"].apply(lambda c: f"{c} ({count_map.get(c, 0)})")

    waterfall_finance = go.Figure(go.Waterfall(
        name="20",
        orientation="v",
        x=df_waterfall["label"],
        textposition="outside",
        y=df_waterfall["Amount"],
        connector={"visible": False},
    ))

    apply_dark_theme(waterfall_finance,
        yaxis=dict(title="Amount"),
        xaxis=dict(title="Category"),
    )


    
    df_cum = df_finance[df_finance["category"] != "pillar2a"]
    df_cum = df_cum[df_cum["category"] != "investment"].copy()
    df_cum_2a = df_finance[df_finance["category"] != "investment"].copy()

    df_kontostand = df_finance_raw[df_finance_raw["category"] != "pillar2a"]
    df_kontostand = df_kontostand.groupby(["year", "month","Date"], as_index=False)[["Amount"]].sum()
    df_kontostand["cum"] = df_kontostand['Amount'].cumsum()
    df_kontostand["cum"] = (df_kontostand["cum"]/1000).round(1)*1000
    df_kontostand = df_kontostand[(df_kontostand["Date"] >= start_date_str) & (df_kontostand["Date"] <= end_date_str)].copy()

    df_cum = df_cum.groupby(["year", "month","Date"], as_index=False)[["Amount"]].sum()  # ,'category_name'
    df_cum["cum"] = df_cum['Amount'].cumsum()
    df_cum["cum"] = (df_cum["cum"]/1000).round(1)*1000
    df_cum["Amount"] = df_cum["Amount"].round(0)

    df_cum_2a = df_cum_2a.groupby(["year", "month","Date"], as_index=False)[["Amount"]].sum()  # ,'category_name'
    df_cum_2a["cum"] = df_cum_2a['Amount'].cumsum()
    df_cum_2a["cum"] = (df_cum_2a["cum"] / 1000).round(1) * 1000

    graph_cum = go.Figure()
    graph_cum.add_trace(
        go.Bar(
            x=df_cum["Date"],
            y=df_cum["Amount"],
            name="Netto monthly",
            textposition="auto",
            yaxis='y1',
        )
    )

    graph_cum.add_trace(
        go.Scatter(
            x=df_cum["Date"],
            y=df_cum["cum"],
            name="cumulative",
            yaxis='y2',
        )
    )
    graph_cum.add_trace(
        go.Scatter(
            x=df_cum_2a["Date"],
            y=df_cum_2a["cum"],
            name="incl. 2a",
            yaxis='y2',
        )
    )

    graph_cum.add_trace(
        go.Scatter(
            x=df_kontostand["Date"],
            y=df_kontostand["cum"],
            name="Konto stand",
            yaxis='y1',
        )
    )
    #graph_cum.update_traces(mode="lines", hovertemplate=None, line=dict(width=2))
    y1_max = math.ceil(max([df_kontostand["cum"].max(), df_cum["Amount"].max()]) / 5000) * 5000
    y1_min = math.floor(min([df_kontostand["cum"].min(), df_cum["Amount"].min()]) / 5000) * 5000
    tickmarks = 5
    y1_tickvals = [y1_min + (y1_max - y1_min) / tickmarks * i for i in range(len([0] * tickmarks))]
    y1_tickvals.append(y1_min)
    y1_tickvals.append(y1_max)
    y2_max = math.ceil(df_cum_2a["cum"].max() / 5000) * 5000
    y2_min = math.floor(df_cum["cum"].min() / 5000) * 5000
    y2_tickvals = [y2_min + (y2_max - y2_min) / tickmarks * i for i in range(len([0] * tickmarks))]
    y2_tickvals.append(y2_min)
    y2_tickvals.append(y2_max)
    apply_dark_theme(graph_cum,
        hovermode="x unified",
        yaxis2=dict(overlaying='y', side='right', range=[y2_min, y2_max], tickvals=y2_tickvals, title="Cumulative worth [CHF]"),
        yaxis=dict(range=[y1_min, y1_max], tickvals=y1_tickvals, title="Monthly [CHF] saved/kontoStand"),
    )


    df_treemap = df_finance_all[df_finance_all["category"] !="salary"].copy()
    df_treemap = df_treemap.groupby(["category","Description"], as_index=False)[["Amount"]].sum()  # ,'category_name'
    df_treemap = df_treemap[df_treemap["Amount"] <= 0].copy()
    df_treemap["Amount"] = abs(df_treemap["Amount"])
    df_treemap.loc[:,"all"] = "all"
    treemap_graph = px.treemap(
        df_treemap,
        path=["all", "category", "Description"],
        values='Amount'
    )

    apply_dark_theme(treemap_graph, margin=dict(l=0, r=0, t=0, b=0))

    df_category_sum = df_finance_raw
    df_category_sum = df_category_sum[~((df_category_sum["category"] == "taxes")
                              | (df_category_sum["category"] == "salary")
                              | (df_category_sum["category"] == "pillar2a")
                                | (df_category_sum["category"] == "investment"))].copy()
    df_category_sum = df_category_sum.groupby(["Date","category"],as_index=False)[["Amount"]].sum()
    df_category_sum = df_category_sum[~((df_category_sum["category"] == "others")&(df_category_sum["Amount"]>=8000))].copy()
    df_category_sum_pivot = pd.pivot(df_category_sum, index=['Date'], columns="category", values="Amount")
    df_category_sum_pivot.reset_index(inplace=True)  # drop frame pivot tables
    df_category_sum_pivot = df_category_sum_pivot.fillna(0)
    df_category_sum_melt = df_category_sum_pivot.melt(id_vars=["Date"], var_name="category", value_name="Amount")
    df_category_sum = df_category_sum_melt
    df_category_sum['3m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=3).mean().reset_index(drop=True)
    df_category_sum['6m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=6).mean().reset_index(drop=True)
    df_category_sum['12m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=12).mean().reset_index(drop=True)
    df_category_sum['24m_roll'] = df_category_sum.groupby('category')['Amount'].rolling(window=24).mean().reset_index(drop=True)

    return waterfall_finance, graph_cum, treemap_graph, df_finance_all.to_dict('records')


@app.callback(
        Output("line_graph", "figure"),
    [
        Input(component_id="include_category", component_property="value"),
        Input(component_id="month_slider", component_property="value"),
        Input(component_id="aggregate_category", component_property="value"),
    ]
)
def area_category_graph(catgory_include, slider_date, aggregate_category):

    start_date_str = months[slider_date[0]] + '-01'
    end_date_str = months[slider_date[1]] + '-01'

    df_finance_raw = _df_category_raw.copy()
    df_finance_raw_all = _df_all_raw.copy()

    #Filtering date
    df_finance = df_finance_raw[(df_finance_raw["Date"] >= start_date_str) & (df_finance_raw["Date"] <= end_date_str)].copy()
    df_finance_all = df_finance_raw_all[(df_finance_raw_all["Date"] >= start_date_str) & (df_finance_raw_all["Date"] <= end_date_str)].copy()

    if ("all" not in catgory_include) & (len(catgory_include)>0):
        df_finance = df_finance[df_finance["category"].isin(catgory_include)].copy()
        df_finance_all = df_finance_all[df_finance_all["category"].isin(catgory_include)].copy()

    #--------------------------------------------------------Line graph------------------------------------------------------------
    if aggregate_category == "yes":
        df_line_graph = df_finance[(df_finance["category"] != "salary") & (df_finance["category"] != "taxes") & (df_finance["category"] != "investment")].copy()
        color = "category"
        y_axis_legend = "Amount spent (CHF)"
    else:
        df_line_graph = df_finance_all[(df_finance_all["category"] != "salary") & (df_finance_all["category"] != "taxes") & (df_finance_all["category"] != "investment")].copy()
        df_line_graph["day"] = 1
        df_line_graph["Date"] = pd.to_datetime(df_line_graph[["year", "month","day"]])
        df_line_graph = df_line_graph.groupby(["Date","Description","category"],as_index=False)[["Amount"]].sum()
        color = "Description"
        threshold_aggregate = 0.01
        y_axis_legend = f"Amount spent (CHF) - Need to be more than {threshold_aggregate*100} % of total"

        total_amount = df_line_graph["Amount"].sum()
    
        df_desc_sum = df_line_graph.groupby("Description", as_index=False)["Amount"].sum()
        df_desc_sum["Percentage"] = (df_desc_sum["Amount"] / total_amount)
        
        top_descriptions = df_desc_sum[df_desc_sum["Percentage"] >= threshold_aggregate]["Description"].tolist()
        
        df_line_graph = df_line_graph[df_line_graph["Description"].isin(top_descriptions)]

    df_line_graph['HoverText'] = df_line_graph.apply(lambda row: f"{row['Date']}: {row['Amount']:.2f}" if row['Amount'] != 0 else "", axis=1)

    # Apply transformations for lowercase and truncation
    df_line_graph[color] = df_line_graph[color].str.lower()
    df_line_graph[color] = df_line_graph[color].apply(lambda x: x[:16])

    # Filter to negative amounts and convert them to positive for display
    df_line_graph = df_line_graph[df_line_graph["Amount"] < 0]
    df_line_graph["Amount"] = abs(df_line_graph["Amount"])

    # Aggregation and rolling calculations for smoothed data
    df_line_graph_sum = df_line_graph.groupby(["Date"], as_index=False)[["Amount"]].sum()
    df_line_graph_sum['Amount_roll_3'] = df_line_graph_sum["Amount"].rolling(window=3).mean().round()
    df_line_graph_sum['Amount_roll_6'] = df_line_graph_sum["Amount"].rolling(window=6).mean().round()
    df_line_graph_sum['Amount_roll_12'] = df_line_graph_sum["Amount"].rolling(window=12).mean().round()

    # Plotting the line graph using Plotly
    graph_line = px.area(df_line_graph, 
                        x="Date", 
                        y="Amount", 
                        color=color, 
                        line_group=color,
                        labels={
                            "Date": "Date",
                            color: "Legend",
                            "Amount": y_axis_legend
                        },
                        category_orders={
                            color: [
                                "housing",
                                "insurance",
                                "transportation",
                                "sport",
                                "restaurant",
                                "food",
                                "entertainment",
                                "others",
                                "health",
                                "clothes",
                                "holidays",
                            ]
                        })

    graph_line.add_trace(
        go.Scatter(
            x=df_line_graph_sum["Date"],
            y=df_line_graph_sum["Amount_roll_3"],
            name="3m avg",
            line=dict(color="black"),
        )
    )
    graph_line.add_trace(
        go.Scatter(
            x=df_line_graph_sum["Date"],
            y=df_line_graph_sum["Amount_roll_6"],
            name="6m avg",
            line=dict(color="black", dash="dot"),
        )
    )
    
    graph_line.add_trace(
        go.Scatter(
            x=df_line_graph_sum["Date"],
            y=df_line_graph_sum["Amount_roll_12"],
            name="12m avg",
            line=dict(color="blue", dash="dash"),
        )
    )

    graph_line.update_traces(mode="lines", hovertemplate=None)
    # Assuming you're adding stacked traces, set the opacity to 1
    graph_line.update_traces(opacity=1)

    apply_dark_theme(graph_line,
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=False, automargin=True),
        yaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=False, title="CHF/months"),
        legend_traceorder="reversed",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.3, font=dict(size=10)),
    )

    return graph_line


def load_prep_data_deepfinder(df):

    df = df.dropna(subset=["Close_CHF"]).copy()

    latest_date = df["Date"].max()

    # Compute the latest total value per stock (use absolute quantity)
    df.loc[:, 'Stock Quantity'] = df['Stock Quantity'].fillna(0)
    df['value'] = df['Stock Quantity'] * df['Close_CHF']
    latest_values = df[df["Date"] == latest_date].groupby("Symbol")["value"].sum()

    # Get top 20 stocks by value
    top20_symbols = latest_values.nlargest(20).index
    df_top20 = df[df["Symbol"].isin(top20_symbols)]
    return top20_symbols, df_top20

def compute_growth(df_stock, start_date):
    df_stock["Date"] = pd.to_datetime(df_stock["Date"])
    df_filtered = df_stock[df_stock["Date"] >= start_date]
    if df_filtered.empty:
        return np.nan
    first = df_filtered.sort_values("Date").iloc[0]["Close_CHF"]
    last = df_filtered.sort_values("Date").iloc[-1]["Close_CHF"]
    return (last - first) / first * 100 if first != 0 else np.nan

def compute_xirr(dates, amounts, guess=0.1):
    """Compute XIRR given lists of dates and cash flow amounts.
    Outflows (investments) should be negative, the final portfolio value positive."""
    dates = pd.to_datetime(dates)
    d0 = dates.min()
    years = np.array([(d - d0).days / 365.25 for d in dates])
    amounts = np.array(amounts, dtype=float)

    def npv(rate):
        return np.sum(amounts / (1 + rate) ** years)

    try:
        result = root(npv, guess)
        if result.success:
            return float(result.x[0])
    except Exception:
        pass
    return np.nan

@app.callback(
    [
        Output("stock_market_macro", "figure"),
        Output("dividends_YtD_value", "children"),        
        Output("dividends_YtD_sub", "children"),
        Output("xirr_value", "children"),

    ],
    [
        Input(component_id="stock_details", component_property="value"),
        Input(component_id="month_slider", component_property="value"),
        Input("app_init", "children"),
    ],
)
def update_compare(stock_details, slider_date, children):

    start_date_str = months[slider_date[0]] + '-01'  # First date
    end_date_str = months[slider_date[1]] + '-01'  # Last date

    IB_degiro_path = path / "IB_degiro.csv"
    snp_path = path / "snp500.csv"
    cash_path = path / "IB_degiro_cash.csv"

    df_IB_degiro = pd.read_csv(IB_degiro_path)
    df_spend_all = _df_all_raw.copy()
    df_snp = pd.read_csv(snp_path)
    df_cash = pd.read_csv(cash_path)
    cash_float = df_cash["Total"].iloc[0]
    stock_threshold_percent = 0.02

    top20_symbols, df_top20 = load_prep_data_deepfinder(df_IB_degiro)

    df_spend_investment = df_spend_all[
        df_spend_all["Description"].str.lower().str.contains("degiro|interactive brockers", case=False, na=False)
    ].copy()

    df_IB_degiro["Date"] = pd.to_datetime(df_IB_degiro["Date"])
    df_spend_investment["day"] = 1
    df_spend_investment["Date"] = pd.to_datetime(df_spend_investment[["year", "month","day"]])
    df_snp["Date"] = pd.to_datetime(df_snp["Date"])

    df_spend_investment_sum = df_spend_investment.groupby(["Date"], as_index=False)[['Amount']].sum()  # ,'category_name'        
    df_spend_investment_sum = df_spend_investment_sum.sort_values(by='Date')
    df_spend_investment_sum['Amount'] = df_spend_investment_sum['Amount'] * -1
    df_spend_investment_sum["Amount_cum"] = df_spend_investment_sum['Amount'].cumsum()

    df_snp_sum = df_snp.groupby(["Date"], as_index=False)[['stock_chf_tot','stock_usd_tot']].sum()  # ,'category_name'        
    df_snp_sum = df_snp_sum.sort_values(by='Date')

    df_IB_degiro_sum = df_IB_degiro.groupby(["Date"], as_index=False)[['Dividends_tot',"total_chf",'total_chf_constant']].sum()  # ,'category_name'        
    df_IB_degiro_sum = pd.merge(df_IB_degiro_sum,df_spend_investment_sum, on = ["Date"],how='outer')
    df_IB_degiro_sum = df_IB_degiro_sum.sort_values(by='Date')

    df_IB_degiro_sum[["Amount_cum", "Dividends_tot", "total_chf",'total_chf_constant']] = df_IB_degiro_sum[["Amount_cum", "Dividends_tot", "total_chf",'total_chf_constant']].ffill()
    current_year = pd.Timestamp.now().year
    df_current_year = df_IB_degiro_sum[df_IB_degiro_sum['Date'].dt.year == current_year].copy()

    ytd_deltas = {}
    for col in ["Dividends_tot"]:
        first_value = df_current_year[col].iloc[0] 
        last_value = df_current_year[col].iloc[-1]  
        ytd_deltas[f'{col}_delta_YTD'] = int(round(last_value - first_value,0))
        ytd_deltas[f'{col}_delta_YTD'] = (f"{ytd_deltas[f'{col}_delta_YTD']:,}") + " CHF"
    
    for col in ["Amount_cum", "total_chf"]:
        first_value = df_current_year[col].iloc[0] 
        last_value = df_current_year[col].iloc[-1]  
        ytd_deltas[f'{col}_delta_YTD'] = int(round(last_value - first_value,0))
    ytd_deltas["equity_YtD"] = "(" + "{:,.0f}".format(round(ytd_deltas["total_chf_delta_YTD"] - ytd_deltas["Amount_cum_delta_YTD"], 0)).replace(",", "'") + " CHF)"
    
    df_IB_degiro_sum["total_chf"] = df_IB_degiro_sum["total_chf"] + float(cash_float)

    # XIRR: cash flows are deposits (negative) + current portfolio value (positive)
    cf_dates = df_spend_investment_sum["Date"].tolist()
    cf_amounts = (df_spend_investment_sum["Amount"] * -1).tolist()  # deposits as negative outflows
    latest_portfolio = df_IB_degiro_sum["total_chf"].iloc[-1]
    cf_dates.append(pd.Timestamp.now())
    cf_amounts.append(latest_portfolio)
    xirr_rate = compute_xirr(cf_dates, cf_amounts)
    xirr_str = f"XIRR: {xirr_rate * 100:.1f}%" if not np.isnan(xirr_rate) else "XIRR: N/A"

    if stock_details == "highlevel":
        df_IB_degiro_sum = df_IB_degiro_sum[(df_IB_degiro_sum["Date"]>= start_date_str) & (df_IB_degiro_sum["Date"]<= end_date_str)]
        df_snp_sum = df_snp_sum[(df_snp_sum["Date"]>= start_date_str) & (df_snp_sum["Date"]<= end_date_str)]
        df_IB_degiro_sum = pd.merge(df_IB_degiro_sum, df_snp_sum, on =["Date"],how = "left")
        df_IB_degiro_sum["stock_chf_tot"] = df_IB_degiro_sum["stock_chf_tot"].ffill()
        df_IB_degiro_sum["stock_usd_tot"] = df_IB_degiro_sum["stock_usd_tot"].ffill()
        graph_degiro_IB = go.Figure()
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["total_chf"],
                name="Degiro_IB_CHF",
                yaxis='y1',
            )
        )
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["total_chf_constant"],
                name="Degiro_IB_USD",
                yaxis='y1',
            )
        )
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["total_chf_constant"] - df_IB_degiro_sum["total_chf"],
                name="Currency loss",
                yaxis='y1',
            )
        )
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["Amount_cum"],
                name="invested",
                yaxis='y1',
            )
        )
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["stock_chf_tot"],
                name="s&p 500",
                yaxis='y1',
            )
        )
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["stock_usd_tot"],
                name="s&p 500 USD",
                yaxis='y1',
            )
        )
        
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["Dividends_tot"],
                name="Dividents CHF",
                yaxis='y2',
            )
        )
        y1_max = math.ceil(max([df_IB_degiro_sum["stock_usd_tot"].max(),df_IB_degiro_sum["total_chf"].max(), df_IB_degiro_sum["Dividends_tot"].max()]) / 20000) * 20000
        y1_min = math.floor(min([df_IB_degiro_sum["stock_usd_tot"].max(), df_IB_degiro_sum["total_chf"].min(), df_IB_degiro_sum["Dividends_tot"].min()]) / 20000) * 20000
        tickmarks = 5
        y1_step = math.ceil((y1_max - y1_min) / tickmarks / 20000) * 20000
        y1_max = y1_min + y1_step * tickmarks
        y1_tickvals = [y1_min + y1_step * i for i in range(tickmarks + 1)]
        y2_max = math.ceil(df_IB_degiro_sum["Dividends_tot"].max() / 10000) * 10000
        y2_min = math.floor(df_IB_degiro_sum["Dividends_tot"].min() / 10000) * 10000
        y2_step = (y2_max - y2_min) / tickmarks
        y2_max = y2_min + y2_step * tickmarks
        y2_tickvals = [y2_min + y2_step * i for i in range(tickmarks + 1)]
        apply_dark_theme(graph_degiro_IB,
            hovermode="x unified",
            yaxis2=dict(overlaying='y', side='right', range=[y2_min, y2_max], tickvals=y2_tickvals, title="Dividends", gridcolor='gray'),
            yaxis=dict(range=[y1_min, y1_max], tickvals=y1_tickvals, title="Invested in stocks and Bonds CHF", gridcolor='gray'),
        )
    elif stock_details == "details_dividends":

        df_IB_degiro_sum = df_IB_degiro.groupby(["Date", "Symbol"], as_index=False)[['Dividends_tot',"total_chf"]].sum()  # ,'category_name'        
        df_IB_degiro_sum = df_IB_degiro_sum.sort_values(by=["Symbol", 'Date'])
        df_IB_degiro_sum["Year"] = df_IB_degiro_sum["Date"].dt.year
        df_IB_degiro_sum["Month"] = df_IB_degiro_sum["Date"].dt.month
        df_IB_degiro_sum["Day"] = 1

        df_IB_degiro_sum = df_IB_degiro_sum[df_IB_degiro_sum != 0]

        df_monthly_avg = df_IB_degiro_sum.groupby(["Symbol", "Year","Month","Day"], as_index=False)[["Dividends_tot"]].mean().round(0)  # ,'category_name'
        df_monthly_avg['Date'] = pd.to_datetime(df_monthly_avg[['Year', 'Month', "Day"]])
        df_monthly_avg.dropna(inplace = True)

        df_monthly_avg = df_monthly_avg.sort_values(by="Dividends_tot", ascending=False)
        
        df_monthly_avg = df_monthly_avg[(df_monthly_avg["Date"]>= start_date_str) & (df_monthly_avg["Date"]<= end_date_str)]
        symbols = df_monthly_avg["Symbol"].unique()  # Get unique countries
        total_sum = df_monthly_avg[df_monthly_avg["Date"] == df_monthly_avg["Date"].max()]["Dividends_tot"].sum()

        graph_degiro_IB = go.Figure()
        for symbol in symbols:
            df_IB_degiro_symbol = df_monthly_avg[df_monthly_avg["Symbol"]== symbol].copy()
            symbol_sum = df_IB_degiro_symbol[df_IB_degiro_symbol["Date"] == df_IB_degiro_symbol["Date"].max()]["Dividends_tot"].sum()
            show_in_legend = bool(symbol_sum >= stock_threshold_percent * total_sum)

            graph_degiro_IB.add_trace(
                go.Bar(
                    x=df_IB_degiro_symbol["Date"],
                    y=df_IB_degiro_symbol["Dividends_tot"],
                    name=symbol,
                    showlegend=show_in_legend,
                )
            )
        apply_dark_theme(graph_degiro_IB, hovermode="x unified", barmode='stack')
    elif stock_details == "deepfinder_inception":
        today = datetime.today()
        start_of_year = datetime(today.year, 1, 1)

        growth_data = []
        for symbol in top20_symbols:
            df_symbol = df_top20[df_top20["Symbol"] == symbol].sort_values("Date")
            inception_growth = compute_growth(df_symbol, df_symbol["Date"].min())
            ytd_growth = compute_growth(df_symbol, start_of_year)
            growth_data.append({
                "Symbol": symbol,
                "Inception Growth %": inception_growth,
                "YTD Growth %": ytd_growth
            })

        df_growth = pd.DataFrame(growth_data).set_index("Symbol").sort_values("Inception Growth %", ascending=False)
        df_growth = df_growth.sort_values("Inception Growth %", ascending=False)
        bar_colors = ["seagreen" if val >= 0 else "crimson" for val in df_growth["Inception Growth %"]]

        # Inception growth chart
        graph_degiro_IB = go.Figure()
        graph_degiro_IB.add_trace(go.Bar(
            x=df_growth.index,
            y=df_growth["Inception Growth %"],
            name="Since Inception Growth (%)",
            marker_color=bar_colors
        ))
        graph_degiro_IB.update_layout(
            title="Top 20 Stocks by Value - Growth Since Inception",
            xaxis_title="Symbol",
            yaxis_title="Growth (%)",
            template="plotly_white"
        )
    elif stock_details =="deepfinder_ytd":
        today = datetime.today()
        start_of_year = datetime(today.year, 1, 1)
        
        growth_data = []
        for symbol in top20_symbols:
            df_symbol = df_top20[df_top20["Symbol"] == symbol].sort_values("Date")
            inception_growth = compute_growth(df_symbol, df_symbol["Date"].min())
            ytd_growth = compute_growth(df_symbol, start_of_year)
            growth_data.append({
                "Symbol": symbol,
                "Inception Growth %": inception_growth,
                "YTD Growth %": ytd_growth
            })

        df_growth = pd.DataFrame(growth_data).set_index("Symbol").sort_values("Inception Growth %", ascending=False)

        df_growth = df_growth.sort_values("YTD Growth %", ascending=False)
        bar_colors = ["seagreen" if val >= 0 else "crimson" for val in df_growth["YTD Growth %"]]

        # YTD growth chart
        df_growth_ytd_sorted = df_growth.sort_values("YTD Growth %", ascending=False)
        graph_degiro_IB = go.Figure()
        graph_degiro_IB.add_trace(go.Bar(
            x=df_growth_ytd_sorted.index,
            y=df_growth_ytd_sorted["YTD Growth %"],
            name="YTD Growth (%)",
            marker_color=bar_colors
        ))
        graph_degiro_IB.update_layout(
            title="Top 20 Stocks by Value - YTD Growth",
            xaxis_title="Symbol",
            yaxis_title="Growth (%)",
            template="plotly_white"
        )

    else:
        
        df_IB_degiro_sum = df_IB_degiro.groupby(["Date", "Symbol"], as_index=False)[['Dividends_tot',"total_chf"]].sum()  # ,'category_name'        
        df_IB_degiro_sum = df_IB_degiro_sum.sort_values(by=["Symbol", 'Date'])
        df_IB_degiro_sum["Year"] = df_IB_degiro_sum["Date"].dt.year
        df_IB_degiro_sum["Month"] = df_IB_degiro_sum["Date"].dt.month
        df_IB_degiro_sum["Day"] = 1

        df_IB_degiro_sum = df_IB_degiro_sum[df_IB_degiro_sum != 0]

        df_monthly_avg = df_IB_degiro_sum.groupby(["Symbol", "Year","Month","Day"], as_index=False)[["total_chf"]].mean().round(0)  # ,'category_name'
        df_monthly_avg['Date'] = pd.to_datetime(df_monthly_avg[['Year', 'Month', "Day"]])
        df_monthly_avg.dropna(inplace = True)

        df_monthly_avg = df_monthly_avg.sort_values(by="total_chf", ascending=False)

        df_monthly_avg = df_monthly_avg[(df_monthly_avg["Date"]>= start_date_str) & (df_monthly_avg["Date"]<= end_date_str)]
        symbols = df_monthly_avg["Symbol"].unique()  # Get unique countries
        total_sum = df_monthly_avg[df_monthly_avg["Date"] == df_monthly_avg["Date"].max()]["total_chf"].sum()

        graph_degiro_IB = go.Figure()
        for symbol in symbols:
            df_IB_degiro_symbol = df_monthly_avg[df_monthly_avg["Symbol"]== symbol].copy()
            symbol_sum = df_IB_degiro_symbol[df_IB_degiro_symbol["Date"] == df_IB_degiro_symbol["Date"].max()]["total_chf"].sum()
            show_in_legend = bool(symbol_sum >= stock_threshold_percent * total_sum)

            graph_degiro_IB.add_trace(
                go.Bar(
                    x=df_IB_degiro_symbol["Date"],
                    y=df_IB_degiro_symbol["total_chf"],
                    name=symbol,
                    showlegend=show_in_legend,

                )
            )

    apply_dark_theme(graph_degiro_IB, hovermode="x unified", barmode='stack')

    return graph_degiro_IB, ytd_deltas["Dividends_tot_delta_YTD"], ytd_deltas["equity_YtD"], xirr_str


@app.callback(
    Output("yoy_graph", "figure"),
    [
        Input("yoy_category", "value"),
        Input("app_init", "children"),
    ],
)
def update_yoy(category, children):
    df = _df_category_raw.copy()
    df = df[df["category"] == category].copy()
    df = df.groupby(["year", "month"], as_index=False)[["Amount"]].sum()
    df["Amount"] = df["Amount"] * -1

    fig = go.Figure()
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for year in sorted(df["year"].unique()):
        df_year = df[df["year"] == year].sort_values("month")
        fig.add_trace(go.Scatter(
            x=[month_labels[m - 1] for m in df_year["month"]],
            y=df_year["Amount"],
            name=str(year),
            mode="lines+markers",
        ))

    # #3 Add average across all years as dotted line
    df_avg = df.groupby("month", as_index=False)["Amount"].mean()
    fig.add_trace(go.Scatter(
        x=[month_labels[m - 1] for m in df_avg["month"]],
        y=df_avg["Amount"],
        name="Avg all years",
        mode="lines",
        line=dict(color="white", dash="dot", width=2),
    ))

    # Overall monthly average as a straight horizontal line
    overall_avg = df["Amount"].mean()
    fig.add_hline(y=overall_avg, line_dash="dash", line_color="yellow", line_width=1,
                  annotation_text=f"Avg: {overall_avg:,.0f} CHF/m",
                  annotation_font_color="yellow")

    apply_dark_theme(fig,
        hovermode="x unified",
        xaxis=dict(title="Month", categoryorder="array", categoryarray=month_labels),
        yaxis=dict(title=f"{category} spend (CHF)"),
    )
    return fig


if __name__ == "__main__":
    app.run(debug=False)
