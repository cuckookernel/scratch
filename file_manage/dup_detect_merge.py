"""Index files in local db and detect duplicates"""
import shutil
import sqlite3
from collections import Counter
from hashlib import md5
from pathlib import Path
from pprint import pformat
from sqlite3 import Connection
from typing import List, Tuple

import pandas as pd
from pandas import DataFrame, Series

# %%
CONFIG = {
    "min_file_size": 10240,
}
# %%

def main():
    # %%
    conn = sqlite3.connect("files.db")
    # %%
    volume_name = 'LH Laptop'
    path = Path('/home/teo/Dokumente/Personales')
    # %%
    volume_name = 'Toshiba Monkey'
    path = Path('/media/teo/TOSHIBA EXT/_sync_laptop/pictures')
    # %%


def _interactive_testing( conn: Connection, volume_name: str, path: Path):
    # %%
    runfile("file_manage/dup_detect_merge.py")
    # %%
    vol = vol_info(conn, volume_name)
    # %%
    index_files_in_path( conn, vol, path)
    # %%


def index_files_in_path( conn: Connection, vol: Series, path: Path):

    vol_path = vol['current_path']

    assert str(path).startswith( vol_path ), f"path: {path} does not start with {vol_path}"
    assert path.exists( ), f"Path doesn't exist: {path}"

    _sync_deleted( conn, vol, path)

    db_files = _get_files_in_db(conn, vol, path)
    updater = Updater(conn, vol, db_files)
    updater.update_path(path)
    # %%


def vol_info( conn: Connection, vol_name: str )-> Series:
    volumes = pd.read_sql(f"select * from volumes where name='{vol_name}'",
                          params=dict(vn=vol_name), con=conn)

    assert len(volumes) == 1, f"Volume '{vol_name}' not found"
    vol = volumes.iloc[0]
    return vol
    # %%


def find_dups( conn: Connection, vol: Series, path: Path):

    db_files = _get_files_in_db(conn, vol, path)

    repeated_md5 = ( db_files.reset_index()
                     .groupby('md5sum')
                     .agg( {'volume_id': 'count',
                            'path': list } )
                     .rename(columns={'volume_id': 'count'})
                     )
    repeated_md5 = repeated_md5[ repeated_md5['count'] > 1 ].sort_values('count')

    dir_pairs = Counter()

    for lst in repeated_md5['path']:
        for i, p1 in enumerate(lst):
            for j in range(i+1, len(lst)):
                p2 = lst[j]
                dir_pairs.update( [(Path(p1).parent, Path(p2).parent)] )

    dir_pairs_df = ( DataFrame( [ {"a": p[0], 'b': p[1], 'cnt': cnt}
                                  for p, cnt in dir_pairs.items() ] )
                     .sort_values('cnt', ascending=False ) )

    return dir_pairs_df
    # %%


def interactive_dups_handling(conn: Connection, vol: Series, path: Path):
    # %%
    vol_path = vol['current_path']

    while True:
        dir_pairs_df = find_dups(conn, vol, path)
        row = dir_pairs_df.iloc[0]
        a_rel_path, b_rel_path = row['a'], row['b']

        a_rel_dir, b_rel_dir = str(a_rel_path), str(b_rel_path)
        a_path = Path(vol_path + a_rel_dir)
        b_path = Path(vol_path + b_rel_dir)

        compare_contents( a_path, b_path )
        print(
            """
            1. merge a into b
            0. merge b into a
            a. eliminate dups a
            b. eliminate dups b
            s. skipa
            q. quit
            """,
        )
        choice = input().strip()
        if choice == '1':
            merge_a_into_b( conn, vol, a_path, b_path )
        elif choice == '0':
            merge_a_into_b( conn, vol, b_path, a_path )
        elif choice == 'a':
            print(f"choice: '{choice}'")
            eliminate_dups_a_to_b( a_path, b_path )
            _sync_deleted(conn, vol, a_path, verbose=True )
        elif choice == 'b':
            eliminate_dups_a_to_b( b_path, a_path )
            _sync_deleted(conn, vol, b_path, verbose=True )
        elif choice == 's':
            continue
        elif choice == 'q':
            break
        else:
            raise ValueError(f"Invalid choice: {choice}")

    # %%


def _interactive_test_compare_merge( conn: Connection, vol: Series):
    # %%
    vol_path = vol['current_path']
    a_dir = '/_sync_laptop/pictures/Pictures/2015_whatsapp_patricia'
    b_dir = '/_sync_laptop/pictures/15_whatsapp_patricia'
    a_path = Path(vol_path + a_dir)
    b_path = Path(vol_path + b_dir)
    # %%
    merge_a_into_b( conn, vol, a_dir, b_dir )
    # %%
    eliminate_dups_a_to_b( a_path, b_path )
    # %%
    _sync_deleted(conn, vol, a_path)
    # %%
    pd.read_sql("""select * from files where path in (
                '/_sync_laptop/pictures/1510_11_Turquia_Patricia/DSCN1615.JPG',
                '/_sync_laptop/pictures/1510_11_Turquia_Patricia/DSCN1623.JPG',
                '/_sync_laptop/pictures/1510_11_Turquia_Patricia/DSCN1635.JPG',
                '/_sync_laptop/pictures/1510_11_Turquia_Patricia/DSCN1638.JPG')
                 """, conn)
    # %%


def compare_contents( a_path: Path, b_path: Path ):
    # %%
    names1 = set( fpath.name for fpath in a_path.glob('*') )

    names2 = set( fpath.name for fpath in b_path.glob('*') )

    print(f'A: {a_path}')
    print(f'B: {b_path}')

    print( f'|A ^ B| = {len(names1.intersection(names2))}')
    print( f'|A \\ B| = {len(names1 - names2)}')
    print( f'|B \\ A| = {len(names2 - names1)}')
    # %%


def merge_a_into_b( conn: Connection, vol: Series, a_path: Path, b_path: Path):
    """Merges all in a into b and deletes b"""
    # %%
    eliminate_dups_a_to_b( a_path, b_path )
    move_a_to_b( conn, a_path, b_path )
    maybe_remove( a_path )
    _sync_deleted(conn, vol, a_path)

    index_files_in_path(conn, vol, b_path )
    # %%


def eliminate_dups_a_to_b( a_path: Path, b_path: Path):
    cnts = dict(files=0, removed_a=0, inexistent_b=0, moved_new_name=0)
    for f1 in a_path.glob('*'):
        if not f1.is_file():
            continue
        cnts['files'] += 1

        f2 = (b_path / f1.name)
        if f2.exists() and f2.is_file():
            bytes1 = f1.open('rb').read()
            bytes2 = f2.open('rb').read()

            if bytes1 == bytes2:
                print(f'{f1.name} also found in B, removing from A')
                f1.unlink()
                cnts['removed_a'] += 1
            else:
                f2b = gen_new_path(f1.name, f2.parent)
                print(f'Moving {f1.name} to {f2.name}')
                shutil.move( f1, f2b )
                cnts['moved_new_name'] += 1
        else:
            cnts['inexistent_b'] += 0

    print( f"eliminate_dups_a_to_b:\na_path: {a_path}\nb_path:{b_path}",
           pformat(cnts) )
    # %%


def gen_new_path( name: str, dir: Path ):
    parts = name.split('.')
    ext = parts[-1]
    base = ".".join( parts[:-1] )

    for i in range(10000):
        new_path = dir / (base + f"_{i}." + ext)
        if not new_path.exists():
            return new_path
    # %%


def move_a_to_b(conn: Connection, a_path: Path, b_path: Path):
    """Move files from a to b, as long as they don't exist there"""
    for f1 in a_path.glob('*'):
        f2 = (b_path / f1.name)
        if not f2.exists():
            shutil.move(f1, f2)
        else:
            print( f'{f2} exists!')
    # %%


def maybe_remove( a_path: Path):
    if len(list(a_path.glob('*'))) == 0:
        print(f'{a_path} is now empty, removing')
        shutil.rmtree(a_path)
    # %%


def _sync_deleted( conn: Connection, vol: Series, path: Path, verbose: bool = False):
    # %%
    db_files = _get_files_in_db(conn, vol, path)
    deleted_files = _find_deleted( db_files, vol['current_path'] )
    print( f"{len(deleted_files)} deleted files" )
    if verbose:
        print( deleted_files )
        print( "before deletion: ",  pd.read_sql("select count(*) from files", conn) )
    # %%
    cursor = conn.cursor()
    deleted_strs = ','.join( f"'{fpath}'" for fpath in deleted_files )
    a = cursor.execute( f"delete from files where cast(volume_id as int)={vol['id']} "
                        f"and path in ({deleted_strs}) ")
    # %%
    conn.commit()

    if verbose:
        print( f"deleted_strs: {deleted_strs[:255]}")
        print("after deletion: ", pd.read_sql("select count(*) from files", conn))
    # %%


def _find_deleted( db_files: DataFrame, vol_path: str ) -> List[Tuple[Path]]:
    result = []
    for path in db_files.index:
        fpath = Path( vol_path + path )
        if not fpath.exists():
            result.append( path )

    return result
    # %%


class Updater:
    def __init__(self, conn: Connection, vol: Series, db_files: DataFrame):
        self.conn = conn
        self.cnts = None
        self.db_files = db_files
        self.volume_id = vol['id']
        self.pending_batch = []
        self.vol_path_len = len(vol['current_path'])

    def update_path( self, path: Path):
        """Recursively scan path"""
        fpaths = list(path.rglob('*'))
        n_fpaths = len(fpaths)
        print(f"{len(fpaths)} files found under {path}")

        self.cnts = dict(non_files=0, too_small=0, unmodified=0, updated=0)
        for i, fpath in enumerate(fpaths):
            if i % 100 == 0:
                print(f"{i:6d} / {n_fpaths}")
                self.write_to_db()
            self._check1(fpath)

        self.write_to_db()
        print(self.cnts)

    def _check1( self, fpath: Path ):
        if not fpath.is_file():
            self.cnts['non_files'] += 1
            return

        stat = fpath.stat()
        if stat.st_size < CONFIG['min_file_size']:
            self.cnts['too_small'] += 1
            return

        modif_ts = stat.st_mtime
        rel_path = str(fpath)[self.vol_path_len:]

        modified = ( rel_path not in self.db_files.index
                     or modif_ts != self.db_files.loc[rel_path]['modif_ts'] )

        if not modified:
            self.cnts['unmodified'] += 1
            return

        size_bytes = stat.st_size

        with fpath.open('rb') as f_in:
            read_size = 10240 if str(fpath).lower().endswith('jpg') else 1024 * 1024
            bytes = f_in.read(read_size)
            md5sum = md5(bytes).hexdigest()

        record = dict(volume_id=self.volume_id,
                      path=str(rel_path),
                      size_bytes=size_bytes,
                      modif_ts=modif_ts,
                      md5sum=md5sum)
        self.pending_batch.append( record )
        self.cnts['updated'] += 1
    # %%

    def write_to_db(self):
        """Write the pending_batch to db"""
        cursor = self.conn.cursor()
        values = [(rec['volume_id'], rec['path'], rec['size_bytes'],
                   rec['modif_ts'], rec['md5sum']) for rec in self.pending_batch]
        cursor.executemany(
            """insert into files (volume_id, path, size_bytes, modif_ts, md5sum)
               values (?,?,?,?,?)
               ON CONFLICT(volume_id, path)
               DO UPDATE SET
                    size_bytes=EXCLUDED.size_bytes,
                    modif_ts=EXCLUDED.modif_ts,
                    md5sum=EXCLUDED.md5sum
               """, values)

        self.conn.commit()
        self.pending_batch = []
    # %%

def _get_files_in_db( conn: Connection, vol: Series, path: Path ) -> pd.DataFrame:
    vol_path_len = len(vol['current_path'])
    rel_path = str(path)[vol_path_len:]
    volume_id = vol['id']

    qry = f"""select modif_ts, path, md5sum, size_bytes,
                                         cast(volume_id as bigint) as volume_id
                                from files
                                where
                                    substr(path,1, {len(rel_path)}) = '{rel_path}'
                                    and cast(volume_id as bigint)={volume_id}
                                """

    print( qry )
    db_files = pd.read_sql( qry, con=conn)

    db_files.set_index('path', inplace=True)
    print(f'files in db (under {path}): {len(db_files)}')

    return db_files
    # %%


def show_files( db: Connection):
    # %%
    pass
    # %%


def _create_tbl_files(conn: Connection):
    # %%
    conn.commit()
    conn.execute("drop table if exists files")

    conn.execute("""
        create table files (
            volume_id bigint,
            path varchar,
            size_bytes bigint,
            modif_ts real,
            md5sum varchar,
            foreign key(volume_id) references volumes(id),
            unique (volume_id, path)
        )
    """)

    conn.commit()

    # %%

def _migrate_(conn: Connection):
    # %%
    conn.execute('alter table files rename to files1')
    conn.commit()
    # %%

    conn.execute("""
        insert into files select cast(volume_id as bigint) as volume_id, path, size_bytes,
        modif_ts, md5sum  from files1
    """)
    # %%
    all = pd.read_sql("select * from files", conn)
    # %%


def show_volumes(conn: Connection):
    """Print volumes to console"""
    # %%
    volumes = pd.read_sql("select * from volumes", conn)
    print(volumes)
    # %%


def _create_volumes(conn: Connection):
    # %%
    conn.execute("drop table if exists volumes")
    conn.execute(
        """
        create table volumes (
            id biginteger primary key,
            name varchar,
            current_path varchar,
            hostname varchar,
            unique(name)
        )
        """,
    )
    conn.execute("insert into volumes (id, name, current_path, hostname)"
               "values (0, 'Toshiba Monkey', '/media/teo/TOSHIBA EXT', null), "
               "       (1, 'LH Laptop', '/', 'golem') ")
    conn.commit()
    # %%
