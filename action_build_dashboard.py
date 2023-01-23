from dash import Dash, html, dcc, Output, Input, dash_table, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from dash_bootstrap_templates import load_figure_template
from plotly.subplots import make_subplots
import plotly.express as px



# TODO: add containers inside chart plot and align to borders
#       add total
#       change filter to dark gray
#       title: remove icon, align left


def _read_sku_data() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parent / 'data' / 'skus_suppliers.csv')


def _read_containers_data() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parent / 'data' / 'containers.csv')


def _read_suppliers_data() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parent / 'data' / 'suppliers.csv')


def costs_chart(sku_v: None | list, supplier_v: None | list, suppliers_df: pd.DataFrame, skus_df: pd.DataFrame):
    # Procurement, Shipment and Total cost indicators
    # layout = go.Layout(width=1200, height=200, margin={'r': 20, 't': 20, 'l': 20, 'b': 20})
    layout = go.Layout(height=100, margin={'r': 0, 't': 20, 'l': 0, 'b': 20})
    fig = go.Figure(layout=layout)
    suppliers_dff = suppliers_df.copy()

    empty = (None, [])

    if (supplier_v not in empty) and (sku_v in empty):
        suppliers_dff = suppliers_dff[suppliers_dff['Supplier Name'].isin(supplier_v)].copy()

        proc_value = sum(suppliers_dff['Procurement Cost'])/1000
        ship_value = sum(suppliers_dff['Shipping Cost'])/1000
        total_value = sum(suppliers_dff['Total Cost'])/1000
        number_containers = sum(suppliers_dff[suppliers_dff['Supplier Name'].isin(supplier_v)]['Number Containers'])

    elif (supplier_v not in empty) and (sku_v not in empty):
        skus_dff = skus_df[skus_df['Supplier Name'].isin(supplier_v)].copy()
        skus_dff = skus_dff[skus_dff['SKU Name'].isin(sku_v)].copy()

        proc_value = sum(skus_dff['Total Cost'])/1000
        ship_value = None
        total_value = None
        number_containers = None

    elif (supplier_v in empty) and (sku_v not in empty):
        skus_dff = skus_df[skus_df['SKU Name'].isin(sku_v)].copy()

        proc_value = sum(skus_dff['Total Cost'])/1000
        ship_value = None
        total_value = None
        number_containers = None

    elif (supplier_v in empty) and (sku_v in empty):
        proc_value = sum(suppliers_dff['Procurement Cost'])/1000
        ship_value = sum(suppliers_dff['Shipping Cost'])/1000
        total_value = sum(suppliers_dff['Total Cost'])/1000
        number_containers = sum(suppliers_dff['Number Containers'])
    
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=proc_value,
            title={'text': "Procurement cost", 'font': {'color': '#49565f'}},
            # number={'prefix': '$', 'valueformat': ',.1f', 'suffix': 'k', 'font': {'size': 50}},
            number={'prefix': '$', 'valueformat': ',.0f', 'suffix': 'k', 'font': {'color': '#49565f'}},
            domain={'x': [0.5, 0.75], 'y': [0, 0.9]},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=ship_value,
            title={'text': "Shipping cost", 'font': {'color': '#49565f'}},
            # number={'prefix': '$', 'valueformat': ',.1f', 'suffix': 'k', 'font': {'size': 50}},
            number={'prefix': '$', 'valueformat': ',.0f', 'suffix': 'k', 'font': {'color': '#49565f'}},
            domain={'x': [0.25, 0.5], 'y': [0, 0.9]},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=total_value,
            # number={'prefix': '$', 'valueformat': ',.1f', 'suffix': 'k', 'font': {'size': 60}},
            number={'prefix': '$', 'valueformat': ',.0f', 'suffix': 'k', 'font': {'color': '#49565f'}},
            # title={'text': "Total cost", 'font': {'size': 35}},
            title={'text': "Total cost", 'font': {'color': '#49565f'}},
            domain={'x': [0.0, 0.25], 'y': [0, 0.9]},
        )
    )
    
    
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=number_containers,
            title={'text': "No. of Containers", 'font': {'color': '#49565f'}},
            domain={'x': [0.75, 1], 'y': [0, 0.9]},
            number={'font': {'color': '#49565f'}},
        )
    )
    

    return fig


def make_subplot(sku_v, supplier_v, skus_df):
    p_colors = px.colors.qualitative.Pastel1

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Quantity of SKU per Supplier", "Cost per SKU per Supplier"))

    empty = (None, [])

    if (sku_v not in empty) and (supplier_v not in empty):
        skus_dff = skus_df[skus_df['SKU Name'].isin(sku_v)].copy()
        skus_dff = skus_dff[skus_dff['Supplier Name'].isin(supplier_v)].copy()

    elif (sku_v not in empty) and (supplier_v in empty):
        skus_dff = skus_df[skus_df['SKU Name'].isin(sku_v)].copy()

    elif (sku_v in empty) and (supplier_v not in empty):
        skus_dff = skus_df[skus_df['Supplier Name'].isin(supplier_v)].copy()
    else:
        skus_dff = skus_df.copy()

    sku_dict = {x: y for x, y in zip(skus_dff['SKU ID'], skus_dff['SKU Name'])}
    color = p_colors
    
    for i in skus_dff['SKU ID'].unique():
        fig.add_trace(
            go.Bar(
                x=skus_dff[skus_dff['SKU ID'] == i]['Supplier Name'],
                y=skus_dff[skus_dff['SKU ID'] == i]['Order Quantity'],
                text=skus_dff[skus_dff['SKU ID'] == i]['Order Quantity'].map("{:,.0f}".format),
                name=sku_dict[i],
                width=0.6,
                # showlegend=False,
                legendgroup='one',
                marker_color=color[i-1],
                insidetextanchor='middle',
            ),
            row=1, col=1
        )

    sum_ord_df = skus_dff.groupby('Supplier Name').agg({'Order Quantity': 'sum'}).reset_index()

    for i in skus_dff['SKU ID'].unique():
        fig.add_trace(
            go.Scatter(
                x=sum_ord_df['Supplier Name'],
                y=sum_ord_df['Order Quantity'],
                text=sum_ord_df['Order Quantity'].map("{:,.0f}".format),
                marker_color= 'rgb(0, 0, 0)',
                mode='text',
                textposition='top center',
                textfont={'size': 13, 'color': '#49565f'},
                showlegend=False,
            ),
            row=1, col=1
        )

    for i in skus_dff['SKU ID'].unique():
        fig.add_trace(
            go.Bar(
                x=skus_dff[skus_dff['SKU ID'] == i]['Supplier Name'],
                y=skus_dff[skus_dff['SKU ID'] == i]['Total Cost'],
                text=skus_dff[skus_dff['SKU ID'] == i]['Total Cost'].map("&#36;{:,.0f}".format),
                name=sku_dict[i],
                showlegend=False,
                width=0.6,
                legendgroup='one',
                marker_color=color[i-1],
                insidetextanchor='middle',
            ),
            row=1,
            col=2
        )

    sum_cost_df = skus_dff.groupby('Supplier Name').agg({'Total Cost': 'sum'}).reset_index()

    for i in skus_dff['SKU ID'].unique():
        fig.add_trace(
            go.Scatter(
                x=sum_cost_df['Supplier Name'],
                y=sum_cost_df['Total Cost'],
                text=sum_cost_df['Total Cost'].map("&#36;{:,.0f}".format),
                marker_color= 'rgb(0, 0, 0)',
                mode='text',
                textposition='top center',
                textfont={'size': 13, 'color': '#49565f'},
                showlegend=False,
            ),
            row=1, col=2
        )
        
    fig.update_yaxes(showticklabels=False)

    fig.update_layout(
        barmode='stack', height=400, margin={'l': 0, 't': 50, 'b': 20},
    ) 

    return fig


def container_utilization(suppliers_df):

    # Utilization per suppliers

    suppliers_dff = suppliers_df.copy()

    layout = go.Layout(
        legend={'itemclick': False, 'itemdoubleclick': False}, height=400, margin={'r': 0, 't': 90, 'l': 20, 'b': 20}
    )

    fig = go.Figure(layout=layout)

    fig.add_trace(
        go.Bar(
            x=suppliers_dff['Supplier Name'],
            y=suppliers_dff['Container Utilization'],
            text=suppliers_dff['Container Utilization'],
            width=0.6,
            # orientation='h',
            marker_color=['rgb(204, 204, 204)']*len(suppliers_dff['Container Utilization'])
        )
    )

    fig.update_yaxes({'range': [0, 1]})
    fig.update_layout(title='Container Utilization per Supplier')

    return fig


def action_build_dashboard():
    suppliers_df = _read_suppliers_data()
    skus_df = _read_sku_data()
    containers_df = _read_containers_data()

    load_figure_template('lumen')
    app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])

    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Span(
                                [
                                    " Projeans Businness Report ",
                                ],
                                className='h1',
                                style={'textAlign': 'center', 'margin-top': '60px', 'margin_bottom': '100px', 'color': '#49565f'},
                            )
                        ],
                        width={'size': 6, 'offset': 1},
                    )
                ],
                justify='center',
                className='my-2 p-4',  # check cheatsheet Utility: Spacing margin my-* for more info
            ),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(id='total_numbers', config={'displayModeBar': False})], width=12),
                    # dbc.Col([dcc.Graph(id='total_containers', config={'displayModeBar': False})], width=2),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label('SKU Name', className='px-2 mb-1 border rounded bg-transparent ', style={'color': '#49565f', 'text-color': '#49565f'}),
                            dcc.Dropdown([x for x in sorted(skus_df['SKU Name'].unique())], multi=True, id='skus_dpdn'),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Label('Supplier Name', className='px-2 mb-1 border rounded bg-transparent', style={'color': '#49565f', 'text-color': '#49565f'}),
                            dcc.Dropdown(
                                [x for x in sorted(suppliers_df['Supplier Name'].unique())], multi=True, id='suppl_dpdn'),
                        ]

                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(id='make_subplot', config={'displayModeBar': False})], width=9),
                    # dbc.Col([dcc.Graph(id='sku_cost_supp', config={'displayModeBar': False})], width=5),
                    dbc.Col([dcc.Graph(id='container_util', config={'displayModeBar': False})], width=3),
                ]
            ),

            
        ]
    )

    @callback(
        Output('total_numbers', 'figure'),
        # Output('total_containers', 'figure'),
        Output('make_subplot', 'figure'),
        # Output('sku_cost_supp', 'figure'),
        Output('container_util', 'figure'),
        # Output('tot_cost_supp', 'figure'),
        Input('skus_dpdn', 'value'),
        Input('suppl_dpdn', 'value'),
    )
    def update_graphs(sku_v, supplier_v):

        fig_numbers = costs_chart(sku_v, supplier_v, suppliers_df, skus_df)
        fig_subplots = make_subplot(sku_v, supplier_v, skus_df)
        fig_cont_util = container_utilization(suppliers_df)

        return fig_numbers, fig_subplots, fig_cont_util

    return app


if __name__ == '__main__':
    app = action_build_dashboard()
    app.run(debug=True)
