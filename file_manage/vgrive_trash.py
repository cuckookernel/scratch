
from collections import defaultdict
from hashlib import md5, sha256
from os import path
from pathlib import Path
from typing import List, Tuple

VGRIVE_LOCAL = Path("/home/teo/_teos_gdrive")
TRASH_PATH = VGRIVE_LOCAL / '.trash'

MP3S_TARGET = '/home/teo/Music'
MP4S_TARGET = '/home/teo/Videos'
# %%

def _main(trash_list):
    restore_exts(trash_list, [".mp3s"], MP3S_TARGET)


def find_trash_dups():
    # %%
    trash_list = list(TRASH_PATH.rglob('*'))
    n_trash = len(trash_list)
    print(len(trash_list), sum(p.stat().st_size for p in  trash_list) / 1e9)
    # %%
    # restore_exts(trash_list, [".mp4"], MP4S_TARGET )
    # %%
    groups = groupby_first_part(trash_list)
    print( sorted( [ (len(v), g) for g, v in groups.items() ] ))
    # %%
    md5_2_paths = defaultdict(list)

    for i, path_ in enumerate(trash_list):
        if path_.is_dir():
            continue
        md5sum = md5(path_.read_bytes()).hexdigest()
        md5_2_paths[md5sum].append(path_)
        if (i + 1) % 100 == 0:
            print( f"{(i + 1)} / {n_trash} ({(i + 1) / n_trash * 100.0:.1f} %)")
    # %%


def purge_dups(md5_2_paths):
    # %%
    n_dups = 0
    dup_size = 0
    deleted_cnt = 0
    space_saved = 0

    for md5sum, paths in md5_2_paths.items():
        n_paths = len(paths)
        if len(paths) < 2:
            continue

        p1 = paths[0]
        if not p1.exists():
            continue
        assert isinstance(p1, Path), f"path: {p1}: {type(p1)}"
        if p1.stat().st_size > 1024:
            n_dups += n_paths - 1
            dup_size += sum( p.stat().st_size for p in paths[1:] if p.exists() )
        else:
            pass
            # print(paths)

        latest = max(paths)
        latest_sha = sha256_from_file(latest)

        for p2 in paths:
            if p2 == latest:
                # print( "same" )
                continue
            if p2.name != p1.name:
                continue

            if not p2.exists():
                continue
            p2_hash = sha256_from_file(p2)

            if p2_hash == latest_sha:
                space_saved += p2.stat().st_size
                p2.unlink()
                deleted_cnt += 1
                if deleted_cnt % 100 == 0:
                    print(f"deleted: {deleted_cnt} space_saved={space_saved}")

                # print(f"Would delete: {p2} and leave: {latest}")

        # print( latest, paths )
        # print( )
    # %%


def groupby_first_part(trash_list: List[Path]):
    groups = defaultdict(list)
    for path_ in trash_list:
        first, _ = extract_first(path_, after=TRASH_PATH.name)
        assert first is not None
        groups[first].append(path_)

    return groups


# %%
def sha256_from_file(path_: Path) -> str:
    assert path_.is_file(), f"path: {path_} symlink: {path_.is_symlink()}"
    return sha256( path_.read_bytes() ).hexdigest()
# %%

def delete_git_files(trash_list: List[Path]):
    # %%
    mp3s = [p for p in trash_list if p.suffix == '.mp3' ]

    for path_ in mp3s:
        path_parts = path_.parts
        if ".git" in path_parts:
            path_.unlink()
    # %%

def restore_exts(trash_list: List[Path],
                 exts: List[str], target_base: Path):
    # %%
    mp3s = [p for p in trash_list
            if p.is_file() and p.suffix in exts  ]
    # %%
    for path_ in mp3s:
        path_parts = path_.parts
        first, first_idx = extract_first(path_, after=TRASH_PATH.name)
        if first is None:
            continue

        new_parts = (first, *path_parts[ first_idx +2:])
        new_path = Path(path.join(*new_parts))
        dest_path = target_base / new_path

        print(path,  dest_path)
        dest_path.parent.mkdir(exist_ok=True, parents=True)

        path_.rename(dest_path)
    # %%

def extract_first(path_, after) -> Tuple[str, int]:
    path_parts = path_.parts
    i = path_parts.index(after)  # find index of '.trash'
    if i < 0:
        return None

    first_idx = path_parts[i + 1].index('_')
    first = path_parts[i + 1][first_idx + 1:]

    print(path_, "\n", first, "\n")
    return first, i+1
    # %%
