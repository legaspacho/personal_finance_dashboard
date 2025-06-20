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
import smbclient
import plotly.express as px
#from app import app
import dash_design_kit as ddk
from theme import theme
import plotly.graph_objects as go
from datetime import datetime, date
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash
from main_pandas_exceptions import main
import math
import os

cwd = os.getcwd()
path = f"{cwd}\\datasets"
username = "usr_vss01"
password = "SaraEm01"

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
app.layout = ddk.App(
    theme=theme,
    children=[
        html.Div(id="app_init"),
        ddk.Block(
            [
                ddk.ControlCard(
                    orientation="horizontal",
                    children=[
                        ddk.ControlItem(
                            dcc.Checklist(
                                id="include_category",
                                value=["all"],
                                options=[{"label": i, "value": i} for i in categories_include],
                                inline=True,
                            ),
                            label="Select categories to include:",
                            style={'display': "inline-block", 'fontSize': '12px'},
                            width=25,
                        ),
                        ddk.ControlItem(
                            dcc.RadioItems(
                                id="spent_aggregation",
                                value="all",
                                labelStyle={'display': 'block'},
                                options=[
                                    {"label": "All time", "value": "all"},
                                    {"label": "Yearly avg", "value": "yearly"},
                                    {"label": "Monthly avg", "value": "monthly"},
                                ],
                            ),
                            label="Select Aggregation method:",
                            style={'fontSize': '12px'}, 
                            width=10,
                        ),
                        
                        ddk.ControlItem(
                            dcc.RadioItems(
                                id="stock_details",
                                value="highlevel",
                                labelStyle={'display': 'block'},
                                options=[
                                    {"label": "High level", "value": "highlevel"},
                                    {"label": "Details Dividends", "value": "details_dividends"},
                                    {"label": "Details Stocks", "value": "details_stocks"},
                                ],
                            ),
                            label="Stock details:",
                            width=10,
                            style={'fontSize': '12px'}, 
                        ),
                        ddk.ControlItem(
                            dcc.RadioItems(
                                id="aggregate_category",
                                value="yes",
                                labelStyle={'display': 'block'},
                                options=[
                                    {"label": "yes", "value": "yes"},
                                    {"label": "no", "value": "no"},
                                ],
                            ),
                            label="Aggregate per category?:",
                            width=10,
                            style={'fontSize': '12px'}, 

                        ),
                        ddk.ControlItem(
                            dcc.RangeSlider(
                                id='month_slider',
                                min= start_month,  # Corresponds to October 2021
                                max= max_value,  # Dynamically set max value
                                value=[start_month , max_value],  # Default value (October 2021)
                                marks={
                                    i: {
                                        'label': month, 
                                        'style': {
                                            'transform': 'rotate(45deg)', 
                                            'whiteSpace': 'nowrap',
                                            'marginLeft': '0px',  # Adjust margin for left alignment
                                            'position': 'absolute',  # Use absolute positioning
                                            'left': f'{(i - 10) / (max_value - 10) * 100}%',  # Align text to the slider point
                                            #'top': '25px',  # Move the text down
                                            'transformOrigin': 'left bottom',  # Rotate around the left side
                                        }
                                    } for i, month in months.items() if i % 2 == 0  # Show every 3rd month
                                },                                
                                step=1,  # Adjust step size
                                included=True,

                            ),
                            label="Select Date from/to:",
                            width=45,
                            style={'fontSize': '12px'},
                        ),
                    ],
                ),
            ],
            width=100,
        ),
        ddk.Row([
                ddk.DataCard(
                    id='saved_ytd',
                    label='Income saved YTD',
                    icon='money-bill',
                    width=25,
                    style={'fontSize': '12px'}, 
                ),
                ddk.DataCard(
                    id='restaurant_YTD',
                    label='Restaurant YTD',
                    icon='glass-martini-alt',
                    width=25,
                    style={'fontSize': '12px'}, 

                ),
            ddk.DataCard(
                id='restaurant_month',
                label='Restaurant current month',
                icon='hamburger',
                width=25,
                style={'fontSize': '12px'}, 
            ),
            ddk.DataCard(
                id='dividends_YtD',
                label='Dividends YtD (equity YtD)',
                icon='piggy-bank',
                width=25,
                style={'fontSize': '12px'}, 

            ),
        ]),
        ddk.Card(
            [
                ddk.CardHeader(
                    title="Monthly spent  (excl. investments)",
                    fullscreen=True,
                ),
                ddk.Graph(id="cumulative"),
            ],
            width=50,
        ),
        ddk.Card(
            [
                ddk.CardHeader(
                    title="IB DEGIRO",
                    fullscreen=True,
                ),
                ddk.Graph(id="stock_market_macro"),
            ],
            width=50,
        ),
        ddk.Card(
            [
                ddk.CardHeader(
                    title="History spent break down",
                    fullscreen=True,
                ),
                ddk.Graph(id="max_overview"),
            ],
            width=50,
        ),
        ddk.Card(
            [
                ddk.CardHeader(
                    title="History spent break down",
                    fullscreen=True,
                ),
                ddk.Graph(id="treemap_graph"),
            ],
            width=50,
        ),
        ddk.Card(
            [
                ddk.CardHeader(
                    title="Monthly spent  (excl. taxes, investments)",
                    fullscreen=True,
                ),
                ddk.Graph(id="line_graph"),
            ],
            width=50,
        ),
        ddk.Card(
            [
                ddk.CardHeader(
                    fullscreen=True,
                ),
                ddk.Graph(id="category_time"),
            ],
            width=50,
        ),
        ddk.Block([
            ddk.Card(
                [
                    ddk.SectionTitle("Individual transactions"),
                    ddk.DataTable(
                        id='new_built_table',
                        columns=(
                            [{'id': p, 'name': p} for p in list_columns]
                        ),
                        data=list_columns,
                        editable=False,
                        page_size=18,
                    ),
                ],
                width=100,
            ),
        ], width=50),
    ],
)


@app.callback(
    [
        Output("saved_ytd", "value"),
        Output("saved_ytd", "sub"),
        Output("restaurant_YTD", "value"),
        Output("restaurant_YTD", "sub"),
        Output("restaurant_month", "value"),
        Output("restaurant_month", "sub"),
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
    [
        Input(component_id="spent_aggregation", component_property="value"),
        Input(component_id="include_category", component_property="value"),
        Input(component_id="month_slider", component_property="value"),
    ]
)
def all_graphs( spent_aggregation, catgory_include, slider_date):

    finance_path = "{path}//spent_category.csv".format(path=path)
    finance_all_path ="{path}//spent_all.csv".format(path=path)

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
        title='Compare change per category',
        xaxis_title='category',
        yaxis_title='Rolling Average €/month',
        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Set plot background color to transparent
        hovermode='x',  # Show hover information only for the x-axis
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="black"
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
        name="20", orientation="v",
        x=df_waterfall["category"],
        textposition="outside",
        y=df_waterfall["Amount"],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    
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
        hoverlabel=dict(font_size=14),
        title_font_size=14,
        yaxis2=dict(overlaying='y',side='right', range=[y2_min, y2_max], tickvals = y2_tickvals,title="Cummulative worth [CHF]",
                                titlefont=dict(
                                    color="black"
                                )),
        yaxis=dict(range=[y1_min, y1_max], tickvals=y1_tickvals, title="Monthly [CHF] saved/kontoStand",
                                titlefont=dict(
                                    color="black"
                                )
        ),
        legend=dict(
            x=0.05,
            y=1,
            xanchor="left", 
            yanchor="top",
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='black',                 
            borderwidth=1
        )
    )

    df_treemap = df_finance_all[df_finance_all["category"] !="salary"].copy()
    df_treemap = df_treemap.groupby(["category","Description"], as_index=False)[["Amount"]].sum()  # ,'category_name'
    df_treemap = df_treemap[df_treemap["Amount"] <= 0].copy()
    df_treemap["Amount"] = abs(df_treemap["Amount"])
    df_treemap.loc[:,"all"] = "all"
    treemap_graph = px.treemap(df_treemap, path=["all", "category","Description"], values='Amount')

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
    graph_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Set plot background color to transparent
        paper_bgcolor='rgba(0,0,0,0)',  # Set paper background color to transparent
        font=dict(family="Arial, sans-serif", size=12, color="black"),  # Customize font
        xaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=False, automargin=True),  # Customize x-axis gridlines with automargin
        yaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=False),  # Customize y-axis gridlines
        legend=dict(font=dict(size=10))
    )

    graph_line.update_layout(
        hovermode="x unified",
        #font_size=14,
        hoverlabel=dict(font_size=14),
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


@app.callback(
    [
        Output("stock_market_macro", "figure"),
        Output("dividends_YtD", "value"),        
        Output("dividends_YtD", "sub"),

    ],
    [
        Input(component_id="stock_details", component_property="value"),
        Input(component_id="month_slider", component_property="value"),
    ],
)
def update_compare(stock_details, slider_date):

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
    print(cash_float)
    stock_threshold_percent = 0.02

    df_spend_investment = df_spend_all[(df_spend_all["Description"] == "Stichting Degiro") | (df_spend_all["Description"] =="interactive brockers llc")].copy()


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
            hoverlabel=dict(font_size=14),
            title_font_size=14,
            yaxis2=dict(overlaying='y',side='right', range=[y2_min, y2_max], tickvals = y2_tickvals,title="Dividends",
                                    titlefont=dict(
                                        color="black"
                                    )),
            yaxis=dict(range=[y1_min, y1_max], tickvals=y1_tickvals, title="Invested in stocks and Bonds CHF",
                                    titlefont=dict(
                                        color="black"
                                    )
            ),
            legend=dict(
                x=0.05,
                y=1,
                xanchor="left", 
                yanchor="top",
                bgcolor='rgba(255, 255, 255, 0.5)',
                bordercolor='black',                 
                borderwidth=1
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
            hoverlabel=dict(font_size=14),
            title_font_size=14,
            legend=dict(
                x=0.05,
                y=1,
                xanchor="left", 
                yanchor="top",
                bgcolor='rgba(255, 255, 255, 0.5)',
                bordercolor='black',                 
                borderwidth=1
            )
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
            hoverlabel=dict(font_size=14),
            title_font_size=14,
            legend=dict(
                x=0.05,
                y=1,
                xanchor="left", 
                yanchor="top",
                bgcolor='rgba(255, 255, 255, 0.5)',
                bordercolor='black',                 
                borderwidth=1
            )
        )


    return graph_degiro_IB, ytd_deltas["Dividends_tot_delta_YTD"], ytd_deltas["equity_YtD"]

if __name__ == "__main__":
    app.run_server(debug=False)
