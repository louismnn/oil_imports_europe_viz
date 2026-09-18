from dash import Dash, dcc, html, Input, Output, callback
import dash_leaflet as dl
import pandas as pd
import numpy as np
import json
from generate_time_series import generate_time_series


app = Dash("Europe Oil Imports")

app.layout = html.Div(
                [
        dcc.Store(id="state", data={"country" : None}),

        html.Div(
            style={"backgroundColor": "black"},
            children = [
                html.H1("Europe Oil Imports",
                            style={
                                "position": "absolute",
                                "top": "10px",
                                "left": "150px",
                                "zIndex": "1000",
                                "margin": "0",
                                "background": "rgba(255,255,255,0)",
                                "padding": "6px 10px",
                                "border-radius": "6px"
                        }),

                dl.Map(
                    id = "map",
                    children = [dl.TileLayer()],
                    center=[56, 10],
                    zoom=6,
                    style={"height": "500px", "width": "100%"}
                ),

                dcc.Graph(
                    id = "time_series",
                    figure = generate_time_series("FR"),
                    className = "custom_time_series",
                    style={"width": "110%", "height": "50vh", "backgroundColor": "black"}
                )

            ], className="custom_second_panel")

    ])


@callback(
    Output("map", "data"),
    Input("map", "clickData"),
    prevent_initial_call = True,
)
def actualisation(click_data):
    if click_data is None:
        return {"country": None}

    latlng = click_data.get("latlng", {})
    lat = latlng.get("lat")
    lon = latlng.get("lng")

    if lat is None or lon is None:
        return {"country": None}

    return {"country": {"lat": lat, "lon": lon}}

if __name__ == "__main__":
    app.run(debug=True, port=3000)