import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import base64
import requests
import os

api_key = os.getenv('GROQ_API_KEY') 

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

app.layout = html.Div([
    dcc.Upload(
        id='upload-txt',
        children=html.Button('Upload TXT File'),
        multiple=False
    ),
    dcc.Textarea(
        id='input',
        style={'width': '100%', 'height': '400px', 'margin': '20px 0'}
    ),
    html.Button('Send', id='send-button'),
    dcc.Loading(
        id="loading",
        type="default",
        children=dcc.Textarea(
            id='output',
            style={'width': '100%', 'height': '400px', 'margin': '20px 0'}
        )
    ),
    html.Button('Save', id='save-button'),
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
    State('input', 'value'),
    prevent_initial_call=True
)
def llm_summary(n_clicks, input_value):
    if not input_value:
        return "Error: Input is empty!"
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers = {"Authorization": f"Bearer {api_key}"},
            json = {
                "model": "deepseek-r1-distill-llama-70b",
                "messages":[
                    {"role": "system", "content": "summarize in one sentence"},
                    {"role": "user", "content": input_value}
                ]
            }
        )
        return response.json()["choices"][0]["message"]["content"]
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