import dash
from dash import dcc, html, Input, Output, State
import requests
import plotly.graph_objs as go
from Components.indicators import components_data
from Components.year import components_years

# Initialize the Dash app
app = dash.Dash(__name__)
server=app.server

# Common styles for layout
HEADER_STYLE = {"textAlign": "center", "color": "#4CAF50", "font-family": "Arial, sans-serif", "margin-bottom": "20px"}
LABEL_STYLE = {"font-weight": "bold", "font-size": "16px"}
BUTTON_STYLE = {
    "background-color": "#4CAF50", "color": "white", "border": "none",
    "padding": "10px 20px", "font-size": "16px", "cursor": "pointer"
}
GRAPH_STYLE = {"margin-top": "30px", "width": "100%", "max-width": "48%", "display": "inline-block"}

# App Layout
app.layout = html.Div([
    html.H1("Economic Indicators", style=HEADER_STYLE),

    # Dropdowns for filtering
    html.Div([
        html.Label("Select Year:", style=LABEL_STYLE),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in components_years['years']],
            placeholder="Select Year",
            style={"margin-bottom": "20px"}
        ),

        html.Label("Select Indicator:", style=LABEL_STYLE),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': indicator, 'value': indicator} for indicator in components_data['indicators']],
            placeholder="Select Indicator",
            style={"margin-bottom": "20px"}
        ),

        # Submit Button
        html.Button('Submit', id='submit-button', n_clicks=0, style=BUTTON_STYLE),
    ], style={"width": "100%", "max-width": "600px", "margin": "auto"}),

    # Graphs
    html.Div([
        dcc.Graph(id='line-graph', style=GRAPH_STYLE),
        dcc.Graph(id='bar-graph', style=GRAPH_STYLE),
    ], style={"display": "flex", "justify-content": "space-around", "flex-wrap": "wrap"})
])

# Callback to fetch and filter data based on dropdown selections
@app.callback(
    [Output('line-graph', 'figure'),
     Output('bar-graph', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [State('year-dropdown', 'value'),
     State('indicator-dropdown', 'value')]
)
def update_graphs(n_clicks, selected_year, selected_indicator):
    if n_clicks > 0:
        # Validate user inputs
        if not selected_year or not selected_indicator:
            print("Year or Indicator not selected. Returning empty graphs.")
            return go.Figure(), go.Figure()

        # Prepare the API payload
        payload = {}
        if selected_year != 'All':
            payload['year'] = selected_year
        if selected_indicator != 'All':
            payload['indicator'] = selected_indicator

        headers = {'Content-Type': 'application/json'}
        api_url = "https://nrpuapi-137b31326fcb.herokuapp.com/api/economic-data/"

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return go.Figure(), go.Figure()

        # Check if data is available
        if not data:
            print("No data returned from the API.")
            return go.Figure(), go.Figure()

        # Prepare graph data
        x_values = [d['Years'] for d in data]

        if selected_indicator == 'All':
            figure_data_line = [
                go.Scatter(x=x_values, y=[d.get(indicator) for d in data], mode='lines+markers', name=indicator)
                for indicator in components_data['indicators']
            ]
            figure_data_bar = [
                go.Bar(x=x_values, y=[d.get(indicator) for d in data], name=indicator)
                for indicator in components_data['indicators']
            ]
        else:
            y_values = [d[selected_indicator] for d in data]
            figure_data_line = [go.Scatter(x=x_values, y=y_values, mode='lines+markers', name=selected_indicator)]
            figure_data_bar = [go.Bar(x=x_values, y=y_values, name=selected_indicator)]

        # Create Line Graph
        line_figure = go.Figure(
            data=figure_data_line,
            layout=go.Layout(
                title=dict(text="Economic Data Line Graph", font=dict(size=20, color="#333"), x=0.5),
                xaxis=dict(title="Year"),
                yaxis=dict(title="Value"),
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#ffffff"
            )
        )

        
        bar_figure = go.Figure(
            data=figure_data_bar,
            layout=go.Layout(
                title=dict(text="Economic Data Bar Graph", font=dict(size=20, color="#333"), x=0.5),
                xaxis=dict(title="Year"),
                yaxis=dict(title="Value"),
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#ffffff"
            )
        )

        return line_figure, bar_figure

    # Return empty graphs by default
    return go.Figure(), go.Figure()

# Run the app
if __name__ == '__main__':
    app.run_server()
