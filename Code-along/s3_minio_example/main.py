import plotly_express as px
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Output, Input, State
from s3pathlib import S3Path, context
import boto3
import pandas as pd
import time
s3url = "s3://my-bucket/simulations/"
time.sleep(6)

s3_client = boto3.client('s3', aws_access_key_id='foobarze', aws_secret_access_key='barfooze', endpoint_url="http://s3service:9000")
context.attach_s3_client(s3_client)

simulation_path =S3Path(s3url)
simulation_path.mkdir(exist_ok=True)

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Dice simulator"),
        html.P("Choose number of dices and number of rolls and enjoy the histogram"),
        dcc.Graph(id="dice-graph"),
        html.Button("Save simulation", id="save-button"),
        html.H2("Number of rolls"),
        dcc.Dropdown(
            id="number_rolls",
            options=[
                {"label": f"{rolls} rolls", "value": rolls}
                for rolls in [10, 100, 1000, 10000]
            ],
            value=100,
        ),
        html.H2("Number of dice"),
        dcc.Slider(
            id="num_dice_slider",
            min=1,
            max=6,
            step=1,
            value=2,
            marks={i: f"{i}" for i in range(1, 7)},
        ),
        dcc.Store(id="simulation-data"),
        dcc.Download(id="download-csv")
    ]
)

@app.callback(
    Output("download-csv", "data"),
    Input("save-button", "n_clicks"),
    State("simulation-data", "data"),
    prevent_initial_call=True
)
def download_csv(n_clicks, data):
    saved_filepath = (simulation_path / f"simulation{n_clicks}.csv")

    if n_clicks:
        csv_string = pd.DataFrame(data).to_csv(index=False)

        with saved_filepath.open("w") as fd:
            fd.write(csv_string)
        return dcc.send_string(csv_string, f"simulation{n_clicks}.csv")
    
    
@app.callback(
    Output("dice-graph", "figure"),
    Input("simulation-data", "data"),
)
def _dice_histogram(dice):
    return px.histogram(np.array(dice).sum(axis=0))

@app.callback(
    Output("simulation-data", "data"),
    Input("num_dice_slider", "value"),
    Input("number_rolls", "value")
)
def _dice_simulation(number_dice=2, number_rolls=100):
    dice = np.random.randint(1,7, size=(number_dice, number_rolls))
    return dice

if __name__ == "__main__":
    print("Hello from Docker container")
    app.run(host = "0.0.0.0", debug=True, port=8081)

