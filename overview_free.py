# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 17:28:20 2021

@author: LHERMITTE_G
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 18:57:39 2021

@author: LHERMITTE_G
"""
import pandas as pd
import plotly.express as px
#from app import app
from theme import theme
import plotly.graph_objects as go
from datetime import datetime, date
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash
from main_pandas_exceptions import main
from dash_table import DataTable
from scipy.optimize import root
import numpy as np
import math
import os

cwd = os.getcwd()
path = f"{cwd}\\datasets"

main(cwd)

# create_dashboard()
app = dash.Dash(__name__, prevent_initial_callbacks=False, external_stylesheets=[dbc.themes.BOOTSTRAP]) # this was introduced in Dash version 1.12.0
server = app.server

list_columns=["year","month","category","fix_variable","Description","Amount"]
categories_include = ["all","taxes","investment","holidays","housing","restaurant","insurance","transportation","sport","others","food","entertainment","clothes","health"]

def generate_months():
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Define the range of months from October 2021 to December 2024
    start_year = 2021
    start_month = 9
    end_year = 2026
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
                                    ),
                                ]
                            ),
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
                                        labelStyle={'display': 'block'},
                                        options=[
                                            {"label": "All time", "value": "all"},
                                            {"label": "Yearly avg", "value": "yearly"},
                                            {"label": "Monthly avg", "value": "monthly"},
                                        ],
                                        className="text-white",
                                    ),
                                ]
                            ),
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
                                        labelStyle={'display': 'block'},
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
                                        labelStyle={'display': 'block'},
                                        options=[
                                            {"label": "yes", "value": "yes"},
                                            {"label": "no", "value": "no"},
                                        ],
                                        className="text-white",
                                    ),
                                ]
                            ),
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
                                    html.Label("Income saved YTD", className="text-white"),
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
                                    html.Div(id='dividends_YtD_value', className='card-text text-white'),  # Placeholder for value
                                    html.Div(id='dividends_YtD_sub', className='card-subtext text-white'),  # Placeholder for sub
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
                                        columns=[{'id': p, 'name': p} for p in list_columns],
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
                                        style_filter={  # Styling the filter/search boxes
                                            'backgroundColor': '#444444',  # Dark gray background for filter boxes
                                            'color': 'white',  # White text color in filter boxes
                                            'border': '1px solid #555555',  # Border styling for the filter boxes
                                            'fontWeight': 'bold',  # Optional: make text bold for better readability
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

    finance_path = "{path}//spent_category.csv".format(path=path)
    finance_all_path ="{path}//spent_all.csv".format(path=path)

    # ---------------------------------------Read files-------------------------------------------
    df_finance_raw = pd.read_csv(finance_path)
    df_finance_raw_all = pd.read_csv(finance_all_path)

    df_finance_raw.loc[:, "day"] = 1
    df_finance_raw["Date"] = pd.to_datetime(df_finance_raw[["year", "month", "day"]])
    #df_finance_raw_all.loc[:, "day"] = 1
    df_finance_raw_all["Date"] = pd.to_datetime(df_finance_raw_all[["year", "month", "day"]])

    #KPIS figures
    df_KPI_saved = df_finance_raw_all[(df_finance_raw_all["category"] != "investment") & (df_finance_raw_all["category"] != "pillar2a") & (df_finance_raw_all["year"] == datetime.today().year)].copy()
    KPI_saved_value = int(df_KPI_saved["Amount"].sum().round())
    KPI_saved_value = (f"{KPI_saved_value:,}") + " CHF"
    df_KPI_saved = df_finance_raw_all[(df_finance_raw_all["category"] != "investment") & (df_finance_raw_all["category"] != "pillar2a") & (df_finance_raw_all["year"] == datetime.today().year -1)].copy()
    df_KPI_saved_Y1 = int(df_KPI_saved["Amount"].sum().round())
    df_KPI_saved_Y1 = (f"{df_KPI_saved_Y1:,}") + " CHF"
    df_KPI_saved_Y1 = "vs {df_KPI_saved_Y1} last year".format(df_KPI_saved_Y1=df_KPI_saved_Y1)

    #KPI resturant
    df_KPI_saved = df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year)].copy()
    KPI_restaurant_value = int(df_KPI_saved["Amount"].sum().round())
    KPI_restaurant_value = (f"{KPI_restaurant_value:,}") + " CHF"
    df_KPI_saved = df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year -1)].copy()
    KPI_restaurant_value_Y1 = int(df_KPI_saved["Amount"].sum().round())
    KPI_restaurant_value_Y1 = (f"{KPI_restaurant_value_Y1:,}") + " CHF"
    KPI_restaurant_value_Y1 = "vs {KPI_restaurant_value_Y1} last year".format(KPI_restaurant_value_Y1=KPI_restaurant_value_Y1)

    #KPIs resturant Monthly
    df_KPI_saved = df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year) \
        & (df_finance_raw_all["month"] == datetime.today().month)].copy()
    KPI_restaurant_M_value = int(df_KPI_saved["Amount"].sum().round())
    KPI_restaurant_M_value = (f"{KPI_restaurant_M_value:,}") + " CHF/m"
    df_KPI_saved = df_finance_raw_all[(df_finance_raw_all["category"] == "restaurant") & (df_finance_raw_all["year"] == datetime.today().year) \
        & (df_finance_raw_all["month"] == datetime.today().month - 1)].copy()
    KPI_restaurant_value_M1 = int(df_KPI_saved["Amount"].sum().round())
    KPI_restaurant_value_M1 = (f"{KPI_restaurant_value_M1:,}") + " CHF"
    KPI_restaurant_value_M1 = "vs {KPI_restaurant_value_M1} last month".format(KPI_restaurant_value_M1=KPI_restaurant_value_M1)

    return KPI_saved_value, df_KPI_saved_Y1, KPI_restaurant_value, KPI_restaurant_value_Y1, KPI_restaurant_M_value, KPI_restaurant_value_M1

@app.callback(
        Output("category_time", "figure"),
        Input("app_init", "children"),

)
def all_graphs( children):

    finance_path = "{path}//spent_category.csv".format(path=path)

    # ---------------------------------------Read files-------------------------------------------
    df_finance_raw = pd.read_csv(finance_path)

    df_finance_raw.loc[:, "day"] = 1
    df_finance_raw["Date"] = pd.to_datetime(df_finance_raw[["year", "month", "day"]])

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

    fig_category.update_layout(
        title=dict(
            font=dict(color='white', size=16)  # White title font
        ),
        xaxis=dict(
            title=dict(
                text='Category',  # X-axis title
                font=dict(color='white')  # White x-axis title font
            ),
            showgrid=True, 
            gridcolor='lightgray', 
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text='Rolling Average €/month',  # Y-axis title
                font=dict(color='white')  # White y-axis title font
            ),
            showgrid=True, 
            gridcolor='lightgray', 
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white'),  # White font for legend text
            bgcolor='rgba(255, 255, 255, 0.1)',  # Slightly transparent white background for legend
            bordercolor='white',
            borderwidth=1
        ),
        plot_bgcolor='#333333',  # Set plot background color to dark gray
        paper_bgcolor='#333333',  # Set paper background color to dark gray
        hovermode='x',  # Show hover information only for the x-axis
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="white"  # White font for general text
        )
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
def all_graphs( spent_aggregation, catgory_include, slider_date):

    finance_path = "{path}//spent_category.csv".format(path=path)
    finance_all_path ="{path}//spent_all.csv".format(path=path)

    start_date_str = months[slider_date[0]] + '-01'  # First date
    end_date_str = months[slider_date[1]] + '-01'  # Last date
    # ---------------------------------------Read files-------------------------------------------
    df_finance_raw = pd.read_csv(finance_path)
    df_finance_raw_all = pd.read_csv(finance_all_path)

    df_finance_raw.loc[:, "day"] = 1
    df_finance_raw["Date"] = pd.to_datetime(df_finance_raw[["year", "month", "day"]])
    #df_finance_raw_all.loc[:, "day"] = 1
    df_finance_raw_all["Date"] = pd.to_datetime(df_finance_raw_all[["year", "month", "day"]])

    #Filtering date
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

    waterfall_finance = go.Figure(go.Waterfall(
        name="20",
        orientation="v",
        x=df_waterfall["category"],
        textposition="outside",
        y=df_waterfall["Amount"],
        connector={"line": {"color": "rgb(200, 200, 200)"}},  # Light grey for the connector line

    ))

    # Update the layout with dark background and white text
    waterfall_finance.update_layout(
        paper_bgcolor='#333333',  # Overall background
        plot_bgcolor='#333333',   # Plot area background

        font=dict(color='white'),  # White font for all text

        hoverlabel=dict(font_size=14, font_color='white'),  # Hover label settings

        title_font_size=14,

        yaxis=dict(
            title="Amount",
            titlefont=dict(color="white"),  # White axis title
            tickfont=dict(color="white")    # White tick labels
        ),

        xaxis=dict(
            title="Category",
            titlefont=dict(color="white"),  # White axis title
            tickfont=dict(color="white")    # White tick labels
        ),

        legend=dict(
            font=dict(color='white')  # Legend font color white if you add a legend
        )
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
    graph_cum.update_layout(
        hovermode="x unified",
        font_size=12,

        # Set the background colors for the overall layout and plot area
        paper_bgcolor='#333333',  # Background of the entire graph
        plot_bgcolor='#333333',   # Background of the plotting area

        font=dict(color='white'),  # General font color set to white

        hoverlabel=dict(font_size=14, font_color='white'),  # White text in hover labels for better visibility

        title_font_size=14,

        yaxis2=dict(
            overlaying='y',
            side='right',
            range=[y2_min, y2_max],
            tickvals=y2_tickvals,
            title="Cumulative worth [CHF]",
            titlefont=dict(color="white"),  # White axis title
            tickfont=dict(color="white")    # White tick labels
        ),

        yaxis=dict(
            range=[y1_min, y1_max],
            tickvals=y1_tickvals,
            title="Monthly [CHF] saved/kontoStand",
            titlefont=dict(color="white"),  # White axis title
            tickfont=dict(color="white")    # White tick labels
        ),

        legend=dict(
            x=0.05,
            y=1,
            xanchor="left",
            yanchor="top",
            bgcolor='rgba(255, 255, 255, 0.2)',  # Transparent white background for the legend
            bordercolor='white',                 # White border for the legend
            borderwidth=1,
            font=dict(color='white')             # White text in the legend for readability
        )
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

    # Update the layout with dark background and white text
    treemap_graph.update_layout(
        paper_bgcolor='#333333',  # Overall background color
        plot_bgcolor='#333333',   # Plot area background color

        font=dict(color='white'),  # White font for all text
        hoverlabel=dict(font_size=14, font_color='white'),  # Hover label settings
        title_font_size=14,

        margin=dict(l=0, r=0, t=0, b=0),  # Remove margins to utilize full container space

        # Update treemap color scheme for better contrast on dark background
        coloraxis_colorbar=dict(
            title="Amount",
            tickfont=dict(color='white'),  # White tick labels on color bar
            titlefont=dict(color='white'),  # White title on color bar
        )
    )

    # Adjust the color scale for the treemap if necessary (optional)
    #treemap_graph.update_traces(marker_colorscale='Viridis', textfont_color='white')

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

    finance_path = "{path}//spent_category.csv".format(path=path)
    finance_all_path ="{path}//spent_all.csv".format(path=path)

    start_date_str = months[slider_date[0]] + '-01'  # First date
    end_date_str = months[slider_date[1]] + '-01'  # Last date
    # ---------------------------------------Read files-------------------------------------------
    df_finance_raw = pd.read_csv(finance_path)
    df_finance_raw_all = pd.read_csv(finance_all_path)

    df_finance_raw.loc[:, "day"] = 1
    df_finance_raw["Date"] = pd.to_datetime(df_finance_raw[["year", "month", "day"]])
    df_finance_raw_all["Date"] = pd.to_datetime(df_finance_raw_all[["year", "month", "day"]])

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

    # Update the layout with your existing style, and ensure no transparency in the legend background
    graph_line.update_layout(
        paper_bgcolor='#333333',  # Set paper background color to dark gray
        plot_bgcolor='#333333',  # Set plot background color to dark gray
        font=dict(family="Arial, sans-serif", size=12, color="white"),  # White font for labels and title
        xaxis=dict(
            showgrid=True, 
            gridcolor='lightgray', 
            zeroline=False, 
            automargin=True,  # Automatically adjust margins for better display
            title=dict(
                font=dict(color='white')  # White font for x-axis title
            )
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='lightgray', 
            zeroline=False, 
            title=dict(
                text="CHF/months",  # Replace with your y-axis title
                font=dict(color='white')  # White font for y-axis title
            )
        ),
        legend=dict(
            font=dict(size=10, color="white"),  # White font for the legend
            bgcolor='rgba(255, 255, 255, 0.1)',  # Slightly transparent white background for legend
            bordercolor='white',  # White border for legend
            borderwidth=1
        )
    )

    graph_line.update_layout(
        hovermode="x unified",  # Unified hover mode for better interaction
        hoverlabel=dict(font_size=14, font_color='white'),  # White font for hover labels
        title_font_size=16,
        legend_traceorder="reversed",
        legend=dict(
            orientation="v", 
            yanchor="top", 
            y=1, 
            xanchor="right", 
            x=1.3  # Move legend further to the right
        )
    )


    return graph_line


def load_prep_data_deepfinder(df):

    df = df.dropna(subset=["Close_CHF"])

    latest_date = df["Date"].max()

    # Compute the latest total value per stock (use absolute quantity)
    df['Stock Quantity'] = df['Stock Quantity'].fillna(0)
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

@app.callback(
    [
        Output("stock_market_macro", "figure"),
        Output("dividends_YtD_value", "children"),        
        Output("dividends_YtD_sub", "children"),

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

    IB_degiro_path = "{path}//IB_degiro.csv".format(path=path)
    df_spend_path = "{path}//spent_all.csv".format(path=path)
    snp_path = "{path}//snp500.csv".format(path=path)
    cash_path = "{path}//IB_degiro_cash.csv".format(path=path)

    # ---------------------------------------Read files-------------------------------------------
    df_IB_degiro = pd.read_csv(IB_degiro_path)
    df_spend_all = pd.read_csv(df_spend_path)
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

    df_snp_sum = df_snp.groupby(["Date"], as_index=False)[['stock_chf_tot']].sum()  # ,'category_name'        
    df_snp_sum = df_snp_sum.sort_values(by='Date')

    df_IB_degiro_sum = df_IB_degiro.groupby(["Date"], as_index=False)[['Dividends_tot',"total_chf"]].sum()  # ,'category_name'        
    df_IB_degiro_sum = pd.merge(df_IB_degiro_sum,df_spend_investment_sum, on = ["Date"],how='outer')
    df_IB_degiro_sum = df_IB_degiro_sum.sort_values(by='Date')

    df_IB_degiro_sum[["Amount_cum", "Dividends_tot", "total_chf"]] = df_IB_degiro_sum[["Amount_cum", "Dividends_tot", "total_chf"]].ffill()

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
        #ytd_deltas[f'{col}_delta_YTD'] = (f"{ytd_deltas[f'{col}_delta_YTD']:,}") + " CHF"
    ytd_deltas["equity_YtD"] = "(" + "{:,.0f}".format(round(ytd_deltas["total_chf_delta_YTD"] - ytd_deltas["Amount_cum_delta_YTD"], 0)).replace(",", "'") + " CHF)"
    # Display the results
    
    df_IB_degiro_sum["total_chf"] = df_IB_degiro_sum["total_chf"] + float(cash_float)

    if stock_details == "highlevel":
        df_IB_degiro_sum = df_IB_degiro_sum[(df_IB_degiro_sum["Date"]>= start_date_str) & (df_IB_degiro_sum["Date"]<= end_date_str)]
        df_snp_sum = df_snp_sum[(df_snp_sum["Date"]>= start_date_str) & (df_snp_sum["Date"]<= end_date_str)]
        df_IB_degiro_sum = pd.merge(df_IB_degiro_sum, df_snp_sum, on =["Date"],how = "left")
        df_IB_degiro_sum["stock_chf_tot"].ffill(inplace=True)
        graph_degiro_IB = go.Figure()
        graph_degiro_IB.add_trace(
            go.Scatter(
                x=df_IB_degiro_sum["Date"],
                y=df_IB_degiro_sum["total_chf"],
                name="Degiro IB CHF",
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
                y=df_IB_degiro_sum["Dividends_tot"],
                name="Dividents CHF",
                yaxis='y2',
            )
        )
        y1_max = math.ceil(max([df_IB_degiro_sum["total_chf"].max(), df_IB_degiro_sum["Dividends_tot"].max()]) / 10000) * 10000
        y1_min = math.floor(min([df_IB_degiro_sum["total_chf"].min(), df_IB_degiro_sum["Dividends_tot"].min()]) / 10000) * 10000
        tickmarks = 5
        y1_tickvals = [y1_min + (y1_max - y1_min) / tickmarks * i for i in range(len([0] * tickmarks))]
        y1_tickvals.append(y1_min)
        y1_tickvals.append(y1_max)
        y2_max = math.ceil(df_IB_degiro_sum["Dividends_tot"].max() / 10000) * 10000
        y2_min = math.floor(df_IB_degiro_sum["Dividends_tot"].min() / 10000) * 10000
        y2_tickvals = [y2_min + (y2_max - y2_min) / tickmarks * i for i in range(len([0] * tickmarks))]
        y2_tickvals.append(y2_min)
        y2_tickvals.append(y2_max)
        graph_degiro_IB.update_layout(
            hovermode="x unified",
            font_size=12,
            hoverlabel=dict(font_size=14, font_color='white'),  # Adjust hover label color
            title_font_size=14,

            # Set the background colors for the overall layout and plot area
            paper_bgcolor='#333333',  # Background of the overall graph
            plot_bgcolor='#333333',   # Background of the plotting area

            font=dict(color='white'),  # Set general text color to white for visibility

            yaxis2=dict(
                overlaying='y',
                side='right',
                range=[y2_min, y2_max],
                tickvals=y2_tickvals,
                title="Dividends",
                titlefont=dict(color="white"),  # White title font for contrast
                tickfont=dict(color="white"),   # White tick font for better visibility
                gridcolor='gray',               # Adjust grid color
            ),

            yaxis=dict(
                range=[y1_min, y1_max],
                tickvals=y1_tickvals,
                title="Invested in stocks and Bonds CHF",
                titlefont=dict(color="white"),  # White title font
                tickfont=dict(color="white"),   # White tick font
                gridcolor='gray',               # Gray grid lines for better visibility
            ),

            legend=dict(
                x=0.05,
                y=1,
                xanchor="left",
                yanchor="top",
                bgcolor='rgba(255, 255, 255, 0.2)',  # Slightly transparent white for the legend background
                bordercolor='white',  # White border for contrast
                borderwidth=1,
                font=dict(color='white')  # White legend text
            )
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
            graph_degiro_IB.update_layout(
                hovermode="x unified",
                barmode='stack',
                font_size=12,

                # Set the background colors for the overall layout and plot area
                paper_bgcolor='#333333',  # Background of the entire graph
                plot_bgcolor='#333333',   # Background of the plotting area

                font=dict(color='white'),  # Set general font color to white for readability

                hoverlabel=dict(font_size=14, font_color='white'),  # Adjust hover label to have white text

                title_font_size=14,

                legend=dict(
                    x=0.05,
                    y=1,
                    xanchor="left",
                    yanchor="top",
                    bgcolor='rgba(255, 255, 255, 0.2)',  # Slightly transparent white for the legend background
                    bordercolor='white',  # White border for better contrast
                    borderwidth=1,
                    font=dict(color='white')  # White text in the legend for visibility
                )
            )
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

    graph_degiro_IB.update_layout(
        hovermode="x unified",
        barmode='stack',
        font_size=12,

        # Set the background colors for the overall layout and plot area
        paper_bgcolor='#333333',  # Background of the entire graph
        plot_bgcolor='#333333',   # Background of the plotting area

        font=dict(color='white'),  # General font color set to white

        hoverlabel=dict(font_size=14, font_color='white'),  # White text in hover labels for readability

        title_font_size=14,

        legend=dict(
            x=0.05,
            y=1,
            xanchor="left",
            yanchor="top",
            bgcolor='rgba(255, 255, 255, 0.2)',  # Transparent white background for the legend
            bordercolor='white',  # White border for contrast
            borderwidth=1,
            font=dict(color='white')  # White text in the legend for readability
        )
    )

    return graph_degiro_IB, ytd_deltas["Dividends_tot_delta_YTD"], ytd_deltas["equity_YtD"]

if __name__ == "__main__":
    app.run(debug=False)
