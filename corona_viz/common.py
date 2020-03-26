import datetime as dt
import os
from pathlib import Path

DateTime = dt.datetime

COVID_DATA_BASE = os.getenv('COVID_DATA_BASE', "/home/teo/git/COVID-19")
RAW_DATA_PATH = Path(f"{COVID_DATA_BASE}/csse_covid_19_data/csse_covid_19_time_series")
PARQUET_PATH = Path( os.getenv('COVID_DATA_BASE', "/home/teo/_data") )

TRANSL = {"Mexico": "México",
          "Italy": "Italia",
          "Spain": "España",
          "US": "EE.UU.",
          "Brazil": "Brasil",
          "Germany": "Alemania",
          "France": "Francia",
          "confirmed": "confirmados",
          "recovered": "recuperados",
          "deaths": "muertes",
          "active": "activos" }

def tstamp_to_dt( tstamp: float ) -> DateTime:
    return dt.datetime.fromtimestamp( tstamp )
