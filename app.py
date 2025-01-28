import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import base64

app = dash.Dash(__name__)

app.layout = html.Div([
    # File upload component
    dcc.Upload(
        id='upload-txt',
        children=html.Button('Upload TXT File'),
        multiple=False
    ),
    
    # Text area for editing
    dcc.Textarea(
        id='text-editor',
        style={'width': '100%', 'height': '400px', 'margin': '20px 0'}
    ),
    
    # Save button
    html.Button('Save Changes', id='save-button'),
    
    # Hidden download component
    dcc.Download(id='download-modified-txt')
])

# Handle file upload and populate textarea
@callback(
    Output('text-editor', 'value'),
    Input('upload-txt', 'contents'),
    State('upload-txt', 'filename')
)
def load_txt_file(contents, filename):
    if contents is None:
        raise PreventUpdate
    
    # Decode TXT file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')
    return decoded  # Populate textarea

# Save modified content as new TXT file
@callback(
    Output('download-modified-txt', 'data'),
    Input('save-button', 'n_clicks'),
    State('text-editor', 'value'),
    prevent_initial_call=True
)
def save_modified_txt(n_clicks, modified_content):
    if not modified_content:
        raise PreventUpdate
    
    # Create downloadable TXT file
    return dict(
        content=modified_content,
        filename="modified_file.txt"
    )

if __name__ == '__main__':
    app.run_server(debug=True)