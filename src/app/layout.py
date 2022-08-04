from dash import dcc, html
import dash_bootstrap_components as dbc

applayout = html.Div([
                dbc.Card([
                    dbc.Row(
                        [
                            dcc.Dropdown(id='QR-agency-dd',
                                         placeholder="Agency"),
                            dcc.Dropdown(id='QR-org-dd',
                                         placeholder="Org"),
                            dbc.Button("Refresh", id='QR-btn', n_clicks=0,
                                       style={'background-color': '#8d5fff',
                                              'color': '#ffffff'},
                                       size='md', className='d-grid gap-*')
                        ],
                        class_name="mb-3",
                    )]),
                dcc.Loading(dbc.Card(id='QR-header', style={'margin-left': 'auto', 'margin-right': 'auto',
                            'text-align': 'center'}), fullscreen=True, type='graph'),
                html.Div(id='QR-Div1', style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center'}),
                html.Div(id='QR-Div2', style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center'}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Div(dcc.Location(id='URL'))
], className='container')
