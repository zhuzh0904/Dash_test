import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import base64
import os
from mistralai import Mistral

# This API key is used as a secret variable in Posit Connect Cloud
api_key = os.getenv('MISTRAL_API_KEY')
client = Mistral(api_key = api_key)

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

app.layout = dbc.Container([
    html.H2("LLM Text Summarizer", className="text-center my-4"),

    dbc.Card([
        dbc.CardHeader("Default Behavior"),
        dbc.CardBody([
            dbc.Textarea(
                id="default-behavior",
                value="summarize in one sentence",
                style={'height': '60px'}
            ),
        ])
    ], className="mb-4 shadow-sm"),

    dbc.Card([
        dbc.CardHeader("Upload File & Select Model"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dcc.Upload(
                        id='upload-txt',
                        children=dbc.Button('Upload TXT File', color="secondary"),
                        multiple=False
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Select(
                        id="dropdown-model",
                        options=[
                            {"label": "mistral-large-latest", "value": "mistral-large-latest"}
                        ]
                    ),
                    width=4
                ),
            ]),
        ])
    ], className="mb-4 shadow-sm"),

    dbc.Card([
        dbc.CardHeader("Input Text"),
        dbc.CardBody([
            dbc.Textarea(
                id='input',
                style={'width': '100%', 'height': '250px'}
            )
        ])
    ], className="mb-4 shadow-sm"),

    dbc.Row([
        dbc.Col(dbc.Button('Send', id='send-button', color="primary", className="w-100"), width=3),
        dbc.Col(dbc.Button('Save', id='save-button', color="success", className="w-100"), width=3),
    ], className="my-3 justify-content-center"),

    dbc.Card([
        dbc.CardHeader("LLM Output"),
        dbc.CardBody([
            dbc.Spinner(
                id="loading",
                color="primary",
                children=dbc.Textarea(
                    id='output',
                    style={'width': '100%', 'height': '250px'}
                )
            )
        ])
    ], className="shadow-sm"),

    dcc.Download(id='download-modified-txt')
], fluid=True)


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
    State('default-behavior', 'value'),
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