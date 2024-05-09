# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                    {'label': 'All Sites', 'value': 'All'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                ],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                            ),
                                html.Br(),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0 KG',
                                                       10000: '10000 KG'},
                                                value=[min_payload, max_payload]),
                                                
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                            ]
                        )

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def update_success_pie_chart(selected_site):
    if selected_site == 'All':
        # Calculate total successful launches count for all sites
        total_success = len(spacex_df[spacex_df['class'] == 1])
        total_failures = len(spacex_df[spacex_df['class'] == 0])
        labels = ['Successful Launches', 'Failed Launches']
        values = [total_success, total_failures]
        title = 'Total Launch Success Rate'
    else:
        # Filter data for the selected site
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = len(site_data[site_data['class'] == 1])
        failure_count = len(site_data[site_data['class'] == 0])
        labels = ['Successful Launches', 'Failed Launches']
        values = [success_count, failure_count]
        title = f'Launch Success Rate at {selected_site}'
        
    fig = px.pie(names=labels, values=values, title=title)
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def update_payload_scatter_chart(selected_site, payload_range):
    if selected_site == 'All':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    
    # Filter data based on selected payload range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title=f'Payload vs. Outcome at {selected_site if selected_site != "All" else "All Sites"}',
                     labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Mission Outcome'},
                     color_discrete_sequence=px.colors.qualitative.Safe)
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
