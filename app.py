import dash
from dash import dcc, html, Input, Output, State
import requests
import plotly.graph_objs as go
from Components.indicators import components_data 
from Components.year import components_years  # Importing the data from components.py

# Initialize the Dash app
app = dash.Dash(__name__)
app.enable_dev_tools(debug=False, dev_tools_ui=False)
server = app.server

# App Layout
app.layout = html.Div([
    html.H1("Economic Indicators ", style={
        "textAlign": "center", 
        "color": "#4CAF50", 
        "font-family": "Arial, sans-serif", 
        "margin-bottom": "20px"
    }),

    # Dropdowns for filtering
    html.Div([
        html.Label("Select Year:", style={"font-weight": "bold", "font-size": "16px"}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in components_years['years']] ,
            placeholder="Select Year",
            style={"margin-bottom": "20px"}
        ),

        html.Label("Select Indicator:", style={"font-weight": "bold", "font-size": "16px"}),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': indicator, 'value': indicator} for indicator in components_data['indicators']] ,
            placeholder="Select Indicator",
            style={"margin-bottom": "20px"}
        ),

        # Submit Button
        html.Button('Submit', id='submit-button', n_clicks=0, style={
            "background-color": "#4CAF50", 
            "color": "white", 
            "border": "none", 
            "padding": "10px 20px", 
            "font-size": "16px", 
            "cursor": "pointer"
        }),
    ], style={"width": "50%", "margin": "auto"}),

    # Line Graph
    html.Div([
        dcc.Graph(id='line-graph', style={"margin-top": "30px", "width": "48%", "display": "inline-block"}),
        dcc.Graph(id='bar-graph', style={"margin-top": "30px", "width": "48%", "display": "inline-block"}),
    ])
])


# Callback to fetch and filter the data based on dropdown selections when the Submit button is clicked
@app.callback(
    [Output('line-graph', 'figure'),
     Output('bar-graph', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [State('year-dropdown', 'value'),
     State('indicator-dropdown', 'value')]
)
def update_graphs(n_clicks, selected_year, selected_indicator):
    if n_clicks > 0:  # Check if the button has been clicked
        print(f"Button clicked {n_clicks} times.")  # Debugging print
        
        # Check if selected values are valid
        if selected_year is None or selected_indicator is None:
            print("Year or Indicator not selected.")
            return go.Figure(), go.Figure()  # Return empty figures if not selected

        # Prepare data for the POST request
        payload = {}
        if selected_year != 'All':
            payload['year'] = selected_year  # Only include year if not 'All'
        if selected_indicator != 'All':
            payload['indicator'] = selected_indicator  # Include indicator if not 'All'
        print(f"Sending payload: {payload}")  # Debugging print to check payload
        
        headers = {'Content-Type': 'application/json'}  # Adding Content-Type header

        # Fetch data from the API using POST request
        api_url = "https://nrpuapi-137b31326fcb.herokuapp.com/api/economic-data/"
        try:
            response = requests.post(api_url, json=payload, headers=headers)  # Send POST request with payload
            response.raise_for_status()  # Raise an error for bad responses
            
            # Extract relevant data
            data = response.json()['data']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return go.Figure(), go.Figure()  # Return empty figures if the API call fails

        # Filter and prepare data for the graphs
        if selected_indicator == 'All':
            figure_data_line = []
            figure_data_bar = []
            for indicator in components_data['indicators']:
                y_values = [d.get(indicator, None) for d in data]
                x_values = [d['Years'] for d in data]
                figure_data_line.append(go.Scatter(
                    x=x_values, y=y_values, mode='lines+markers', name=indicator
                ))
                figure_data_bar.append(go.Bar(
                    x=x_values, y=y_values, name=indicator
                ))
        else:
            y_values = [d[selected_indicator] for d in data]
            x_values = [d['Years'] for d in data]
            figure_data_line = [go.Scatter(
                x=x_values, y=y_values, mode='lines+markers', name=selected_indicator
            )]
            figure_data_bar = [go.Bar(
                x=x_values, y=y_values, name=selected_indicator
            )]

        # Create Line Graph
        line_figure = go.Figure(
            data=figure_data_line,
            layout=go.Layout(
                title=dict(
                    text="Economic Data Line Graph",
                    font=dict(size=20, color="#333"),
                    x=0.5
                ),
                xaxis=dict(title="Year"),
                yaxis=dict(title="Value"),
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#ffffff",
            )
        )

        # Create Bar Graph
        bar_figure = go.Figure(
            data=figure_data_bar,
            layout=go.Layout(
                title=dict(
                    text="Economic Data Bar Graph",
                    font=dict(size=20, color="#333"),
                    x=0.5
                ),
                xaxis=dict(title="Year"),
                yaxis=dict(title="Value"),
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#ffffff",
            )
        )

        return line_figure, bar_figure

    return go.Figure(), go.Figure()  # Return empty figures if the button hasn't been clicked


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
