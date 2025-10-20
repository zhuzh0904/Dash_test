import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import base64
import requests
import os
from mistralai import Mistral

# This API key is used as a secret variable in Posit Connect Cloud
api_key = os.getenv('MISTRAL_API_KEY')
client = Mistral(api_key = api_key)

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

app.layout = html.Div([
    html.H3("LLM Text Summarizer", style={'textAlign': 'left'}),
    html.H5("Default behavior:", style={'textAlign': 'left'}),
    dbc.Textarea(
        id = "deault-behavior",
        value = "summarize in one sentence",
        style={'width': '40%', 'height': '10px', 'margin': '20px 0'}
    ),
    html.H5("Upload TXT file (Optional) and select model:", style={'textAlign': 'left'}),
    dbc.Row([
        dbc.Col(
            dcc.Upload(
                id='upload-txt',
                children=dbc.Button('Upload TXT File'),
                multiple=False
            ),
            width="auto"
        ),
        dbc.Col(
            dbc.Select(
                id = "dropdown-model",
                options=[
                    {"label": "mistral-large-latest", "value": "mistral-large-latest"}
                ]
            ),
            width=4
        )
    ]),
    dbc.Textarea(
        id='input',
        style={'width': '100%', 'height': '400px', 'margin': '20px 0'}
    ),
    dbc.Button('Send', id='send-button'),
    dbc.Spinner(
        id="loading",
        color="primary",
        children=dbc.Textarea(
            id='output',
            style={'width': '100%', 'height': '400px', 'margin': '20px 0'}
        )
    ),
    dbc.Button('Save', id='save-button'),
    dcc.Download(id='download-modified-txt')
])

# Load uploaded file
@callback(
    Output('input', 'value'),
    Input('upload-txt', 'contents'),
    State('upload-txt', 'filename'),
    prevent_initial_call=True
)
def load_txt_file(contents, filename):
    if not contents or not filename.endswith('.txt'):
        return no_update
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"Upload error: {e}")
        return no_update

# Handle LLM request on button click
@callback(
    Output('output', 'value'),
    Input('send-button', 'n_clicks'),
    State('deault-behavior', 'value'),
    State('dropdown-model', 'value'),
    State('input', 'value'),
    prevent_initial_call=True
)
def llm_summary(n_clicks, default_behavior, model_value, input_value):
    if not input_value:
        return "Error: Input is empty!"
    
    try:
        response = client.chat.complete(
            model = model_value,
            messages = [
                {
                    "role": "system", "content": default_behavior
                },
                {
                    "role": "user", "content": input_value
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {str(e)}"

# Save output
@callback(
    Output('download-modified-txt', 'data'),
    Input('save-button', 'n_clicks'),
    State('output', 'value'),
    prevent_initial_call=True
)
def save_modified_txt(n_clicks, modified_content):
    if not modified_content:
        return no_update
    return dict(content=modified_content, filename="modified_file.txt")

if __name__ == '__main__':
    app.run_server(debug=True)