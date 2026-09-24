from datetime import datetime, timedelta
from countryinfo import CountryInfo
from geopy.distance import geodesic
import dash_leaflet as dl
from pathlib import Path
import pandas as pd
import numpy as np
import json
import os


directory = Path(__file__).resolve().parent

csv_path = directory / r"assets\eurostat_data.csv"
csv_raw_path = directory / r"assets\eurostat_data_raw.csv"
database_path = directory / r"assets\database.json"


with open(database_path, "r") as f:
    DATABASE_COUNTRIES_NAME = json.load(f).get("country_name", {})

def get_country_name(iso_code : str) -> str:
        return DATABASE_COUNTRIES_NAME.get(iso_code, "")



def order_datas(country_iso_code: str):
    """
    Return a DataFrame with the data ordered by time_period (index) and partner_iso_code (columns) for a specific country.
    """

    df = pd.read_csv(csv_path)

    df = df[df["consumer_iso_code"] == country_iso_code]
    df["time_period"] = pd.to_datetime(df["time_period"], format="%Y-%m", errors="coerce")

    df = df.pivot_table(index="time_period", columns="partner_iso_code", values="obs_value", aggfunc="sum")

    my_set = set()

    for i in range(len(df)):
        second_highest_value = df.iloc[i].nlargest(n=3)
        my_set.update(second_highest_value.index)

    df_final = df[list(my_set)]

    df_final["OTHERS"] = df.sum(axis=1) - df_final[list(my_set)].sum(axis=1)
    del df
    df_final.index = df_final.index.strftime("%Y-%m")

    weights_last_period = df_final.iloc[-1].div(df_final.iloc[-1].sum(axis=0)).dropna()
    weights_last_period = dict(((weights_last_period * 25000).pow(2/5) - 10).round(0))

    return df_final, {v:int(k) for v,k in weights_last_period.items()}



def fetch_datas_from_eurostat() -> None:
    """
    Fetch data from the Eurostat API and return it as a pandas DataFrame.
    """
    print("Getting the datas from Eurostat 🔜")

    start = "2024-01"
    end = (datetime.now() - timedelta(days=62)).strftime("%Y-%m")

    dt = np.flip(np.arange(start, end, dtype='datetime64[M]'))
    dt = np.array2string(dt, separator=",").replace("'", "").replace("\n", "").replace(" ", "")

    api_url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/nrg_ti_oilm/1.0/*.*.*.*.*?c[freq]=M&c[siec]=O4000&c[partner]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,LI,NO,CH,UK,BA,ME,MD,MK,GE,AL,RS,TR,UA,XK,AD,BY,GI,RU,EX_YU_OTH,EX_SU_OTH,EUR_OTH,AO,CM,CG,CD,GQ,GA,ST,DJ,ER,ET,KE,MG,MU,MZ,UG,TZ,DZ,EG,LY,MA,SS,SD,TN,BW,NA,ZA,BJ,CV,CI,GH,GW,LR,MR,NE,NG,SN,SL,TG,AFR_OTH,CA,US,AW,BS,BB,VG,CU,CW,DO,JM,AN,TT,AME_LAT,BZ,CR,GT,HN,MX,PA,AR,BO,BR,CL,CO,EC,GY,PE,UY,VE,AME_OTH,KZ,KG,TJ,TM,UZ,CN,HK,JP,MN,KP,KR,TW,BD,IN,IR,NP,PK,LK,BN,KH,ID,LA,MY,MM,PH,SG,TH,TL,VN,AM,AZ,BH,IQ,IL,JO,KW,LB,OM,QA,SA,SY,AE,YE,ASI_NME,ASI_NME_OTH,ASI_OTH,AU,NZ,NC,PG,MH,NSP&c[unit]=THS_T&c[geo]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,NO,UK,ME,MD,MK,GE,AL,RS,TR&c[TIME_PERIOD]={dt.replace("[", "").replace("]", "")}&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name"

    df = pd.read_csv(api_url, usecols=["partner", "geo", "TIME_PERIOD", 'OBS_VALUE'])

    df.to_csv(csv_path, index=False, encoding="utf-8")
    print("Datas sucessfully downloaded ✅")



def normalize_datas() -> None:

    df = pd.read_csv(csv_raw_path, encoding="utf-8")

    df.columns = ["partner_iso_code", "consumer_iso_code", "time_period", "obs_value"]

    df["obs_value"] = df["obs_value"].astype(str)
    df = df[df["obs_value"] != "0.0"]
    df["obs_value"] = df["obs_value"].astype(float)

    c = ['EX_YU_OTH', 'EX_SU_OTH', 'EUR_OTH', 'AFR_OTH', 'AME_LAT', 'AME_OTH', 'ASI_NME', 'ASI_NME_OTH', 'ASI_OTH', 'NSP']

    df = df.replace(c, "OTHERS")
    df = df.replace("EL", "GR")
    df = df.replace("XK", "AL")

    df = df.groupby(by=["partner_iso_code", "consumer_iso_code", "time_period"]).sum()
    df.reset_index(inplace=True)

    df.to_csv(csv_path, index=False)

    if "eurostat_data.csv" in os.listdir("assets"):
        os.remove(csv_raw_path)



with open(database_path, "r") as f:
    DATABASE_COUNTRIES_EUROPE = json.load(f).get("country_europe", {})

def check_iso_code(iso_code: str) -> None | str:
    return iso_code if iso_code in DATABASE_COUNTRIES_EUROPE else None



def shorten_line(A: list | tuple, B: list | tuple, distance_before_B=100):
    """
    A and B: (latitude, longitude)
    distance_before_B: distance in km
    """

    total_distance = geodesic(A, B).km

    if distance_before_B >= total_distance:
        return A

    ratio = (total_distance - distance_before_B) / total_distance

    new_lat = A[0] + ratio * (B[0] - A[0])
    new_lon = A[1] + ratio * (B[1] - A[1])

    return new_lat, new_lon



def curved_line(A: list | tuple, B: list | tuple, curvature=0.2, n=100) -> list:

    B = shorten_line(A, B)

    A = np.array(A)
    B = np.array(B)

    M = (A + B) / 2
    d = B - A

    perp = np.array([-d[1], d[0]])
    perp = perp / np.linalg.norm(perp)

    C = M + curvature * np.linalg.norm(d) * perp

    t = np.linspace(0, 1, n)

    points = (
        (1-t[:, None])**2 * A
        + 2*(1-t[:, None])*t[:, None] * C
        + t[:, None]**2 * B
    )

    return points.tolist(), B.tolist()



def generate_polylines(iso_code_consumer: str,
                       weights: dict,
                       curvature=0.1
                       ) -> list[dl.Polyline]:

    colors = [
        '#30123b', '#4145ab', '#4675ed', '#39a2fc', '#1bcfd4', '#24eca6',
        '#61fc6c', '#a4fc3b', '#d1e834', '#f3c63a', '#fe9b2d', '#f36315',
        '#d93806','#b11901', '#7a0402', '#440154', '#482878', '#3e4989',
        '#31688e','#26828e','#1f9e89', '#35b779', '#6ece58', '#b5de2b',
        '#fde725']

    lines_objects = []

    f = CountryInfo(iso_code_consumer).latlng()

    for country, color in zip(weights.keys(), colors):

        if country not in ["OTHERS", iso_code_consumer]:

            r = CountryInfo(country).latlng()
            vec, b = curved_line(r, f, curvature=curvature)

            lines_objects.append(dl.CircleMarker(
                center=b,
                radius=25,
                fillOpacity=0,
                opacity=0,
                children=[
                    dl.Tooltip(f"""Oil import route: {get_country_name(country)}"""),
                ],
            ))

            lines_objects.append(
                dl.PolylineDecorator(
                    children=dl.Polyline(positions=vec,
                                         color=color,
                                         pathOptions={
                                            "weight" : weights.get(country, 10),
                                            "lineCap": "butt",
                                            "lineJoin": "miter",
                                            "opacity": 1,
                                        }
                                    ),
                    patterns = [{
                                "offset" : "100%",
                                "repeat" : "0",
                                "arrowHead" : {
                                    "pixelSize" : weights.get(country, 10), 
                                    "polygon" : False,
                                    "headAngle": 65,
                                    "pathOptions" : {
                                        "stroke" : True,
                                        "color" : color,
                                        "weight": weights.get(country, 10),
                                        "opacity": 1,
                                        "lineCap": "butt",
                                        "lineJoin": "miter",
                                        }
                                    }
                            }]
                    )
                )

    return lines_objects



def _reverse_coords(coords: list):
    if isinstance(coords[0], (int, float)):
        coords.reverse()
    else:
        for coord in coords:
            _reverse_coords(coord)



def reverse_coordinates(iso_code: str) -> list:

    country_shape_path = directory / f"assets\\countries\\10m\\{iso_code}.geojson"

    with open(country_shape_path, "r", encoding="utf-8") as file:
        geo = json.load(file)["features"]

        final_coordinates = []

        for i in geo:
            for coords in i["geometry"]["coordinates"]:
                _reverse_coords(coords)

            final_coordinates.append(i["geometry"]["coordinates"])

        return final_coordinates
