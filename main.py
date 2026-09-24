from generate_time_series import generate_time_series, generate_init_graph
from dash import Dash, dcc, html, Input, Output, callback
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import dash_leaflet as dl
from pathlib import Path
import pandas as pd
import util



directory = Path(__file__).resolve().parent
csv_path = directory / r"assets\eurostat_data.csv"

try:
    df = pd.read_csv(csv_path, encoding="utf-8", usecols=["time_period"])
    maximum_date = pd.to_datetime(df["time_period"], format="%Y-%m").max()

    if maximum_date < (datetime.now() - timedelta(days=120)):
        raise FileNotFoundError

except FileNotFoundError:
    a = util.fetch_datas_from_eurostat()
    b = util.normalize_datas()


app = Dash("Europe Oil Imports")
geolocator = Nominatim(user_agent="oil_europe_viz")


app.layout = html.Div(
            children = [

                dcc.Store(id="store_datas", data={"country" : None}, storage_type="memory"),

                html.H1("Europe Oil Imports", className="custom_title"),

                dl.Map(
                    id = "map",
                    className="custom_map",
                    children = [dl.TileLayer(), dl.ScaleControl(position="bottomleft")],
                    center=[56, 10],
                    zoom=6,
                    zoomControl=False,
                    zoomDelta=6,
                    maxZoom=6,
                    minZoom=6,
                    maxBounds=[[34, -25], [72, 45]]
                ),

                dcc.Graph(
                    id = "time_series",
                    figure = generate_init_graph(),
                    className="custom_time_series"
                )
            ],
            className="main_panel",
        )



@callback(
    Output("store_datas", "data"),
    Input("map", "clickData"),
    prevent_initial_call = True
)
def store_datas(click_data):

    if click_data is None:
        return None

    latlng = tuple(click_data.get("latlng", {}).values())

    try:
        location = geolocator.reverse(latlng)
        iso_code = location.raw["address"].get("country_code", {}).upper()
        return util.check_iso_code(iso_code)

    except AttributeError:
        return None



@callback(
    Output("time_series", "figure"),
    Output("map", "children"),
    Input("store_datas", "data"),
    prevent_initial_call = True,
)
def actualisation(iso_code):

    if iso_code is None:
        return generate_init_graph(), [dl.TileLayer(), dl.ScaleControl(position="bottomleft")]

    fig, weights = generate_time_series(iso_code)
    polyline_list = util.generate_polylines(iso_code_consumer=iso_code, weights=weights)

    return fig, [dl.TileLayer(),
                 dl.ScaleControl(position="bottomleft"),
                 dl.Polygon(positions=util.reverse_coordinates(iso_code),
                            color="blue", opacity=0.3, fillColor='blue', fillOpacity=0.3)
                 ] + polyline_list


if __name__ == "__main__":
    app.run(debug=False, port=3000, host="0.0.0.0")
