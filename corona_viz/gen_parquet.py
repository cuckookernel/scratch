from importlib import reload
import corona_viz.etl as etl
from corona_viz.common import PARQUET_PATH, tstamp_to_dt
# %%

def main():
    # %%
    reload( etl )
    max_mtime = etl.max_raw_data_mtime()
    print( f'max_raw_data_mtime = {tstamp_to_dt(max_mtime)}')
    data = etl.load_data()
    data['date'] = data['date'].astype(str)
    last_date = data[data.n_confirmed.notnull()]['date'].max()
    print( f'last_date = {last_date}')
    # %%
    fp = PARQUET_PATH / f'df_{last_date}.parquet'

    if not fp.exists() or max_mtime > fp.stat().st_mtime:
        data.to_parquet(fp)
        print(f'Generated {fp} : {tstamp_to_dt(fp.stat().st_mtime)}')
    else:
        print(f'Not regenerating parquet as {fp} is from {tstamp_to_dt(fp.stat().st_mtime)}')

if __name__ == '__main__':
    main()