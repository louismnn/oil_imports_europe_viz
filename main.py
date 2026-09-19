from dash import Dash, dcc, html, Input, Output, callback
from generate_time_series import generate_time_series
from generate_points import curved_line
from geopy.geocoders import Nominatim
from  countryinfo import CountryInfo
import dash_leaflet as dl
import json
import util



class GenerateMap:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="oil_europe_viz")
        self.iso_code = None
        self.patterns = [{
            "offset" : "100%",
            "repeat" : "0",
            "arrowHead" : {
                "pixelSize" : 15, 
                "polygon" : False,
                "headAngle": 65,
                "pathOptions" : {
                    "stroke" : True
                    }
                }
        }]

    def get_datas(self, latlng: tuple) -> str | None:

        location = self.geolocator.reverse(latlng)

        try:
            iso_code_temp = location.raw["address"].get("country_code", {}).upper()
            print(iso_code_temp)

        except AttributeError:
            return self.iso_code

        with open(r"assets\database.json", "r") as f:
            d = json.load(f).get("country_europe", [])

            if iso_code_temp in list(d.keys()):
                self.iso_code = iso_code_temp
                self.df = util.order_datas(self.iso_code)
            else:
                raise ValueError("Country is unknow")

            return self.iso_code

    def generate_polylines(self, curvature=0.1) -> list[dl.Polyline]:

        list_partners = list(self.df.columns)
        list_partners.remove("TOTAL")
        list_partners.remove("OTHERS")

        lines_objects = []

        f = CountryInfo(self.iso_code).latlng()

        for country in list_partners:

            r = CountryInfo(country).latlng()
            vec = curved_line(r, f, curvature=curvature)

            lines_objects.append(
                dl.PolylineDecorator(
                    children=dl.Polyline(positions=vec),
                    patterns=self.patterns
                    )
                )

        return lines_objects



Map = GenerateMap()
app = Dash("Europe Oil Imports")

app.layout = html.Div(
            children = [
                html.H1("Europe Oil Imports", className="custom_title"),

                dl.Map(
                    id = "map",
                    className="custom_map",
                    children = [dl.TileLayer()],
                    center=[56, 10],
                    zoom=6
                ),

                dcc.Graph(
                    id = "time_series",
                    figure = generate_time_series(None),
                    style={"width":"80%","height": "20vh"}
                )
            ],
            className="main_panel",
        )


@callback(
    Output("time_series", "figure"),
    Output("map", "children"),
    Input("map", "clickData"),
    prevent_initial_call = True,
)
def actualisation(click_data):

    if click_data is None:
        return generate_time_series(Map.iso_code), [dl.TileLayer()]

    latlng = tuple(click_data.get("latlng", {}).values())

    iso_code = Map.get_datas(latlng=latlng)

    if iso_code == None:
        return generate_time_series(Map.iso_code), [dl.TileLayer()]

    polyline_list = Map.generate_polylines()

    return generate_time_series(iso_code), [dl.TileLayer()] + polyline_list

if __name__ == "__main__":
    app.run(debug=True)