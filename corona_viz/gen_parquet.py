from pathlib import Path
from importlib import reload
import corona_viz.etl as etl

from corona_viz.common import PARQUET_PATH, tstamp_to_dt
# %%


def gen_parquet_world():
    """Load csv data with load_data"""
    # %%
    reload(etl)

    max_mtime = etl.max_raw_data_mtime()
    print( f'gen_parquet_world: max_raw_data_mtime = {tstamp_to_dt(max_mtime)}')
    data = etl.load_data_world()
    data['date'] = data['date'].astype(str)
    last_date = data[data.n_confirmed.notnull()]['date'].max()
    print( f'gen_parquet_world: last_date = {last_date}')
    # %%
    fp = PARQUET_PATH / f'world/df_{last_date}.parquet'
    code_mtime = Path('corona_viz/etl.py').stat().st_mtime

    if ( not fp.exists() or max_mtime > fp.stat().st_mtime
         or code_mtime > fp.stat().st_mtime ):
        data.to_parquet(fp)
        print(f'Generated {fp} : {tstamp_to_dt(fp.stat().st_mtime)}')
    else:
        print(f'Not regenerating parquet as {fp} is from {tstamp_to_dt(fp.stat().st_mtime)}')
    # %%


def main():
    """Gen parquet for world and for colombia"""
    # %%
    try:
        gen_parquet_world()
    except Exception as e:
        print( "\n\n\nFailed generating world parquet!\n\n", e)
    # %%
    etl.get_and_save_data_col_v2()
    # %%


if __name__ == '__main__':
    main()
