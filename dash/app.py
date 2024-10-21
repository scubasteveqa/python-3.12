from dash import Dash, Output, Input, html, callback
import base64
from PIL import Image
import requests
from io import BytesIO
from voxel_world import Volume, Surface, Agent, Sequence
import vnoise
import numpy as np
import random

url = 'https://i.giphy.com/okfvUCpgArv3y.webp'
response = requests.get(url)
pil_img = Image.open(BytesIO(response.content))

app = Dash(__name__)

app.layout = html.Div([
    html.Button('Regenerate world', id='submit-val', style={'position':'absolute'}),
    html.Img(src=pil_img, id='voxel-world', style={'width':'100%'}),                          
])

@callback(
    Output('voxel-world', 'src'),
    Input('submit-val', 'n_clicks'),
)
def update_output(value):
    """ Generate voxel world """
    volume = Volume(Volume.purlin_matrix(16))
    surf = Surface(volume);
    agents = [Agent(surf, mask) for mask in Sequence.snake(grid_size=16, num_steps=100)];
    seq = Sequence(agents);
    seq2 = seq.apply_bg(volume)
    gif_stream = seq2.frames_to_gif_stream().getvalue()

    return 'data:image/png;base64,' + base64.b64encode(gif_stream).decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
