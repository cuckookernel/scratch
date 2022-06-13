"""
rename files in a diretory so that timestamp appears first and resolution is attached at the end
"""

from PIL import Image

from pathlib import Path
import re

REGEX1 = r'(?P<prefix>img|pano|vid)_(?P<ts1>\d+)_(?P<ts2>\d+)(?P<rest>.*)?\.(?P<ext>jpg|mov|mp4)'

REGEX_OK = r'(?P<ts1>\d+)_(?P<ts2>\d+)(?P<rest>.*)?\.(?P<ext>jpg|mov|mp4)'
# %%


def mass_rename_jpgs(path: Path):
    # %%
    files = list(path.glob('*'))
    # fpath = files[0]
    ignored_cnt = 0

    for fpath in files:
        if fpath.stat().st_size == 0:
            print( f'Skiping file of size 0: {fname}' )
            continue
            # fpath.unlink()

        fname = fpath.name
        mch = re.match(REGEX1, fname, re.IGNORECASE)
        if bool(mch):
            new_fname = _make_new_fname(fpath, mch)
            new_fpath = fpath.parent / new_fname
            if new_fpath.exists():
                print( f'Already there: {new_fpath}, skipping...')

            else:
                print( f'{fname} -> {new_fname}')
                fpath.rename( new_fpath )
        elif re.match(REGEX_OK, fname, re.IGNORECASE):
            ignored_cnt += 1
        else:
            raise ValueError(f'not matched fname: {fname}')

    print( ignored_cnt )
    # %%


def _make_new_fname( fpath, mch: re.Match ) -> str:

    file_ext = mch['ext'].lower()
    dic = mch.groupdict().copy()

    if file_ext in ('jpg'):

        with Image.open( fpath ) as image:
            dic.update( {'width': image.width, 'height': image.height} )

        new_fname = "{ts1}_{ts2}_{prefix}{rest}_w{width}_h{height}.{ext}".format( **dic )

    elif file_ext in ('mp4'):

        new_fname = "{ts1}_{ts2}_{prefix}{rest}.{ext}".format( **dic )

    else:
        raise ValueError(f'Unknown ext: {file_ext} : {fpath}')

    return new_fname
    # %%


def _interactive_testing():
    path = Path("/home/teo/Dokumente/personal/Photos/2021-Celular-DCIM-Camera/")
