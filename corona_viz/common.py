"""Shared routines and constants"""

import datetime as dt
import glob
import os
from pathlib import Path
from typing import Dict, NamedTuple, Optional

import pandas as pd

DF = pd.DataFrame
DateTime = dt.datetime
Date = dt.date
class DataCacheRec(NamedTuple):
    mtime: int
    data: DF
    fp: Path


COVID_DATA_BASE = os.getenv('COVID_DATA_BASE', "/home/teo/git/COVID-19")
RAW_DATA_PATH = Path(f"{COVID_DATA_BASE}/csse_covid_19_data/csse_covid_19_time_series")
PARQUET_PATH = Path( os.getenv('COVID_PARQUETS_DIR', "/home/teo/_data/covid") )

TRANSL = {"World": "Mundo",
          "Mexico": "México",
          "Italy": "Italia",
          "Spain": "España",
          "US": "EE.UU.",
          "Brazil": "Brasil",
          "Germany": "Alemania",
          "France": "Francia",
          "confirmed": "confirmados",
          "recovered": "recuperados",
          "deaths": "muertes",
          "active": "activos"}


def tstamp_to_dt( tstamp: float ) -> DateTime:
    """Unix timestamp to python datetime"""
    return dt.datetime.fromtimestamp( tstamp )


def get_data(cache: Dict[Date, DataCacheRec],
             glob_str: str,
             date: Optional[Date] = None,
             date_col: str = 'date') -> DataCacheRec:
    """Get DF for the given date or the most recent one if not provided"""
    if date is not None:
        tmpl = glob_str.replace('*', '{date}')
        fp = Path( tmpl.format( date=date ) )
        if not fp.exists():
            raise RuntimeError(f'No data for {date}')
    else:
        date = dt.date.today()
        fp = most_recent_parquet( glob_str )

    # % At this point fp exists
    if date in cache and fp.stat().st_mtime <= cache[date].mtime:
        print(f"retrieving data from memory cache:\n \tdate={date} "
              f" {cache[date].fp} {cache[date].mtime} - file:{fp.stat().st_mtime}")
    else:
        # %
        mtime = fp.stat().st_mtime
        tstamp = tstamp_to_dt(mtime)
        print(f"date in cache {date in cache} retrieving data from disk:\nf {fp} ({tstamp})")
        if date in cache:
            print(f"cache {tstamp_to_dt(cache[date].mtime)}")
        # %
        data = pd.read_parquet(fp)
        data[date_col] = pd.to_datetime(data[date_col])
        cache[date] = DataCacheRec(mtime=mtime, data=data, fp=fp)

    return cache[date]
    # %%


def most_recent_parquet( glob_str: str ) -> Path:
    """Most recent parquet matching a glob"""
    fnames = glob.glob( str(PARQUET_PATH / glob_str) )
    print( f'{len(fnames)} parquet data files found')

    if len(fnames) > 0:
        def mtime_path( fname: str ):
            path = PARQUET_PATH / fname
            mtime = path.stat().st_mtime
            return mtime, path

        f_mtime = sorted( [mtime_path(fname) for fname in fnames] )
        fp = f_mtime[-1][1]
        return fp
    else:
        raise RuntimeError('Need to run gen_parquet.py first...')
    # %%
