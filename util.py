import pandas as pd
from datetime import datetime, timedelta
import json


def get_country_name(iso_code : str) -> str:
    with open(r"assets\database.json", "r") as f:
        data = json.load(f)
        return data["country_name"][iso_code]


def order_datas(country_iso_code: str) -> pd.DataFrame:
    """
    Return a DataFrame with the data ordered by time_period (index) and partner_iso_code (columns) for a specific country.
    """

    df_init = pd.read_csv(r"assets\eurostat_data.csv")

    df_init = df_init[df_init["consumer_iso_code"] == country_iso_code]
    df_init = df_init[["time_period", "partner_iso_code", "obs_value"]]

    partner_iso_codes = df_init["partner_iso_code"].unique().tolist()
    data_index = df_init["time_period"].unique().tolist()

    if "EL" in partner_iso_codes:
        partner_iso_codes = ["GR" if x == "EL" else x for x in partner_iso_codes]
    
    df = pd.DataFrame(index=data_index, columns=partner_iso_codes)

    for j in data_index:
        vec = df_init[df_init["time_period"] == j]
        df.loc[j] = pd.Series(vec["obs_value"].values, index=vec["partner_iso_code"].values)

    df = df.astype("float64", errors="ignore")

    for i in ["CN_X_HK", "EU27_2020"]:
        if i in list(df.columns):
            del df[i]

    my_set  = set()

    for i in range(len(df)):
        second_highest_value = df.iloc[i].nlargest(n=5)
        my_set.update(second_highest_value.index)

    my_list = list(my_set)
    df = df[my_list]

    df["OTHERS"] =  2 * df["TOTAL"] - df[my_list].sum(axis=1)

    if "XK" in list(df.columns):
        if "AL" in list(df.columns):
            df["AL"] = df["AL"] + df["XK"]
            del df["XK"]
        else:
            df.columns = df.columns.str.replace("XK", "AL")

    columns_to_remove = {"ASI_OTH", "AME_OTH", "AFR_OTH", "ASI_NME", "EX_SU_OTH", "NSP"}

    if set(df.columns) - columns_to_remove != set(df.columns):
        for col in list(columns_to_remove):
            if col in list(df.columns):
                df["OTHERS"] = df["OTHERS"] + df[col]
                del df[col]

    return df


def fetch_data_from_eurostat() -> None:
    """
    Fetch data from the Eurostat API and return it as a pandas DataFrame.
    """

    start = datetime.strptime("2024-01", "%Y-%m") # 01-2008
    end = (datetime.now()-timedelta(days=30)).strftime("%Y-%m")

    d = pd.date_range(start=start, end=end, freq='ME')
    dates_list = list(d.strftime("%Y-%m"))[::-1]

    api_url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/nrg_ti_oilm/1.0/*.*.*.*.*?c[freq]=M&c[siec]=O4000&c[partner]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,LI,NO,CH,UK,BA,ME,MD,MK,GE,AL,RS,TR,UA,XK,AD,BY,GI,RU,EX_YU_OTH,EX_SU_OTH,EUR_OTH,AO,CM,CG,CD,GQ,GA,ST,DJ,ER,ET,KE,MG,MU,MZ,UG,TZ,DZ,EG,LY,MA,SS,SD,TN,BW,NA,ZA,BJ,CV,CI,GH,GW,LR,MR,NE,NG,SN,SL,TG,AFR_OTH,CA,US,AW,BS,BB,VG,CU,CW,DO,JM,AN,TT,AME_LAT,BZ,CR,GT,HN,MX,PA,AR,BO,BR,CL,CO,EC,GY,PE,UY,VE,AME_OTH,KZ,KG,TJ,TM,UZ,CN,CN_X_HK,HK,JP,MN,KP,KR,TW,BD,IN,IR,NP,PK,LK,BN,KH,ID,LA,MY,MM,PH,SG,TH,TL,VN,AM,AZ,BH,IQ,IL,JO,KW,LB,OM,QA,SA,SY,AE,YE,ASI_NME,ASI_NME_OTH,ASI_OTH,AU,NZ,NC,PG,MH,TOTAL,NSP&c[unit]=THS_T&c[geo]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,NO,UK,ME,MD,MK,GE,AL,RS,TR&c[TIME_PERIOD]={','.join(dates_list)}&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name"

    df = pd.read_csv(api_url, usecols=["partner", "geo", "TIME_PERIOD", 'OBS_VALUE'])
    df.columns = ["partner_iso_code", "consumer_iso_code", "time_period", "obs_value"]
    df.to_csv(r"assets\eurostat_data.csv")



def get_simple_keys(data: str | dict, parent_key='product_type') -> list:
    result = []
    for key in data[parent_key].keys():
            result.append(key)
    return result




