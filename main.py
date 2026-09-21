from dash import Dash, dcc, html, Input, Output, callback
from generate_time_series import generate_time_series
from geopy.geocoders import Nominatim
import dash_leaflet as dl
import util
import pandas as pd
from datetime import datetime, timedelta


try:
    df = pd.read_csv(r"assets\eurostat_data.csv", encoding="utf-8")
    maximum_date = pd.to_datetime(df["time_period"], format="%Y-%m").max()

    if maximum_date < (datetime.now() - timedelta(days=120)):
        raise FileNotFoundError

except FileNotFoundError:
    util.fetch_datas_from_eurostat()
    util.normalize_datas()


app = Dash("Europe Oil Imports")
geolocator = Nominatim(user_agent="oil_europe_viz")


app.layout = html.Div(
            children = [

                dcc.Store(id="store_datas", data={"country" : None}, storage_type="memory"),

                html.H1("Europe Oil Imports", className="custom_title"),

                dl.Map(
                    id = "map",
                    className="custom_map",
                    children = [dl.TileLayer()],
                    center=[56, 10],
                    boxZoom=False,
                    zoom=6
                ),

                dcc.Graph(
                    id = "time_series",
                    figure = generate_time_series(),
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
        return generate_time_series(), [dl.TileLayer()]

    datas = util.order_datas(iso_code)
    countries = list(datas.columns)
    countries.remove('OTHERS')

    polyline_list = util.generate_polylines(iso_code_consumer=iso_code,
                                            iso_code_partner=countries)

    return generate_time_series(iso_code), [dl.TileLayer()] + polyline_list



if __name__ == "__main__":
    app.run(debug=True)