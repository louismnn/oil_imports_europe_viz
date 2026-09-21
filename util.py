import pandas as pd
from datetime import datetime, timedelta
import json
import os
import numpy as np
from countryinfo import CountryInfo
import dash_leaflet as dl



def get_country_name(iso_code : str) -> str:
    with open(r"assets\database.json", "r") as f:
        data = json.load(f)
        return data["country_name"][iso_code]



def order_datas(country_iso_code: str) -> pd.DataFrame:
    """
    Return a DataFrame with the data ordered by time_period (index) and partner_iso_code (columns) for a specific country.
    """

    df = pd.read_csv(r"assets\eurostat_data.csv")

    df = df[df["consumer_iso_code"] == country_iso_code]
    df["time_period"] = pd.to_datetime(df["time_period"], format="%Y-%m", errors="coerce")

    df = df.pivot_table(index="time_period", columns="partner_iso_code", values="obs_value", aggfunc="sum")

    my_set = set()

    for i in range(len(df)):
        second_highest_value = df.iloc[i].nlargest(n=4)
        my_set.update(second_highest_value.index)

    df_final = df[list(my_set)]

    df_final["OTHERS"] = df.sum(axis=1) - df_final.sum(axis=1)
    df_final.index = df_final.index.strftime("%Y-%m")

    return df_final



def fetch_datas_from_eurostat() -> None:
    """
    Fetch data from the Eurostat API and return it as a pandas DataFrame.
    """

    start = "2024-01"
    end = (datetime.now() - timedelta(days=62)).strftime("%Y-%m")

    dt = np.flip(np.arange(start, end, dtype='datetime64[M]'))
    dt = np.array2string(dt, separator=",").replace("'", "").replace("\n", "").replace(" ", "")

    api_url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/nrg_ti_oilm/1.0/*.*.*.*.*?c[freq]=M&c[siec]=O4000&c[partner]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,LI,NO,CH,UK,BA,ME,MD,MK,GE,AL,RS,TR,UA,XK,AD,BY,GI,RU,EX_YU_OTH,EX_SU_OTH,EUR_OTH,AO,CM,CG,CD,GQ,GA,ST,DJ,ER,ET,KE,MG,MU,MZ,UG,TZ,DZ,EG,LY,MA,SS,SD,TN,BW,NA,ZA,BJ,CV,CI,GH,GW,LR,MR,NE,NG,SN,SL,TG,AFR_OTH,CA,US,AW,BS,BB,VG,CU,CW,DO,JM,AN,TT,AME_LAT,BZ,CR,GT,HN,MX,PA,AR,BO,BR,CL,CO,EC,GY,PE,UY,VE,AME_OTH,KZ,KG,TJ,TM,UZ,CN,HK,JP,MN,KP,KR,TW,BD,IN,IR,NP,PK,LK,BN,KH,ID,LA,MY,MM,PH,SG,TH,TL,VN,AM,AZ,BH,IQ,IL,JO,KW,LB,OM,QA,SA,SY,AE,YE,ASI_NME,ASI_NME_OTH,ASI_OTH,AU,NZ,NC,PG,MH,NSP&c[unit]=THS_T&c[geo]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,NO,UK,ME,MD,MK,GE,AL,RS,TR&c[TIME_PERIOD]={dt.replace("[", "").replace("]", "")}&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name"

    df = pd.read_csv(api_url, usecols=["partner", "geo", "TIME_PERIOD", 'OBS_VALUE'])

    df.to_csv(r"assets\eurostat_data_raw.csv", index=False, encoding="utf-8")



def normalize_datas() -> None:

    df = pd.read_csv(r"assets\eurostat_data.csv")

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

    df.to_csv(r"assets\eurostat_data.csv", index=False)

    if "eurostat_data.csv" in os.listdir("assets"):
        os.remove(r"assets\eurostat_data_raw.csv")



def check_iso_code(iso_code: str) -> None | str:

    with open(r"assets\database.json", "r") as f:
        d = json.load(f).get("country_europe", {})

        if iso_code in list(d.keys()):
            return iso_code
        else:
            return None



def curved_line(A, B, curvature=0.2, n=100):

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

    return points.tolist()



def generate_polylines(iso_code_consumer: str, iso_code_partner: list, curvature=0.1) -> list[dl.Polyline]:

    lines_objects = []

    f = CountryInfo(iso_code_consumer).latlng()

    for country in iso_code_partner:

        r = CountryInfo(country).latlng()
        vec = curved_line(r, f, curvature=curvature)

        lines_objects.append(
            dl.PolylineDecorator(
                children=dl.Polyline(positions=vec),
                patterns = [{
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
                )
            )

    return lines_objects