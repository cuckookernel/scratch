
import shutil
from collections import defaultdict
from hashlib import md5
from pathlib import Path

# FileKey = (filename, size)
FileKey = tuple[str, int]
# %%


def main():
    """Index files in two directories and delete files under path_a that are found anywhere
    under path_b
    """
    # %%
    path_a = Path('/home/teo/gdrive_clone.trash')
    index_a = index_path(path_a)
    size_a_mb = calc_total_size(index_a) / 1e6
    print(size_a_mb)
    # %%
    empty_dirs = find_empty_dirs(path_a)
    print(len(empty_dirs))
    for dir in empty_dirs:
        dir.rmdir()
    # %%
    # path_b = Path('/home/teo/gdrive_rclone')
    path_b = Path('/media/teo/T7')
    index_b = index_path(path_b)
    size_b_mb = calc_total_size(index_b) / 1e6
    print(size_b_mb)
    # %% Interactive testing
    parent_path = path_a
    # %%
    # index_b = index_a
    # %%
    delete_dups(index_a, index_b)
# %%


def _interactive_testing(index_a, index_b):
    runfile("file_manage/gdrive_sync/simple_dup_detect_delete.py")
    delete_dups(index_a, index_b)
    # %%
    all_files = list(Path('/home/teo/gdrive_rclone.trash').glob('*'))
    dst_dir = Path('/home/teo/Documents/_STAGED_FOR_UPLOAD_TO_DRIVE/HVs/linkedin-scraped')
    assert dst_dir.is_dir() and dst_dir.exists()
    # %%
    for file in all_files:
        if file.is_dir() or not file.exists() or file.suffix not in ['.txt', '.html']:
            continue
        txt_ver = dst_dir / (file.stem + '.txt')
        html_ver = file.parent / (file.stem + '.html')
        if txt_ver.exists() and html_ver.exists():
            print(txt_ver)
            print(html_ver)
            shutil.move(html_ver, dst_dir)
    # %%


def delete_dups(index_a: dict[FileKey, set[Path]], index_b: dict[FileKey, set[Path]]):
    # %%
    deleted_cnt = 0
    saved_space = 0
    # %%
    for key_a, paths_a in index_a.items():
        size = key_a[1]
        if key_a in index_b:
            paths_a1 = [path_a for path_a in paths_a if path_a.exists() and not path_a.is_dir()]
            md5s_a = {path_a: md5(path_a.read_bytes()).hexdigest() for path_a in paths_a1}
            md5s_b = group_by_md5(index_b[key_a])

            for path_a, md5a in md5s_a.items():
                if md5a in md5s_b:
                    paths_b = md5s_b[md5a]
                    if paths_b == {path_a}:
                        continue
                    to_delete = shall_delete(path_a, paths_b)
                    if to_delete:
                        deleted_cnt += 1
                        saved_space += size

    print(deleted_cnt, saved_space/1e6)
    # %%


AUTO_DEL_EXTS = {
    '.pdf', '.ps', '.dvi', '.mobi', '.epub', '.doc',
    '.txt', '.tex', '.log', '.tex~',
    '.rtf', '.djvu', '.srt', '.djv', '.idx',
    '.ppt', '.pptx', '.pdx', '.xls', '.xlsx', '.odt', '.docx', '.wps', '.html', '.xml', '.prc',
    '.png', '.bmp', '.jpg', '.jpeg', '.gif', '.svg',
    '.wma', '.wav',
    '.ini', '.json', '.csv', '.dat',  '.sas7bdat', '.bin', '.nfo', '.egp',
    '.mp3', '.mp4',  '.flac', '.flv',
    '.htm', '.chm', '.cab', '.zip',  '.rar', '.jar', '.class', '.classpath', '.save', '.backup',
    '.index', '.prefs',
    '.gz', '.tar', '.tgz', '.scala', '.sbt', '.sas', '.mak', '.mac', '.url',
    '.r', '.rmd', '.sh', '.exe', '.c', '.cpp', '.h', '.py', '.js', '.vcproj',
    '.css', '.shx', '.shp', '.sbn', '.dbf', '.prj', '.m', '.v', '.v#', '.ml', '.mli' }


def shall_delete(path_a: Path, paths_b: set[Path]) -> bool:
    #  if 'xxxxx' in { '.pdf', '.ps', '.mobi', '.epub', '.doc',
    if path_a.name.lower().endswith('thumbs.db'):
        return False
    if path_a.name.lower() == 'makefile':
        return True

    if path_a.suffix.lower() in AUTO_DEL_EXTS:
        print("auto deleting:", path_a, f"found in: {paths_b}")
        return True
    else:
        print(f"path_a.suffix: {path_a.suffix}")
        paths_b1 = {path_b for path_b in paths_b if path_b != path_a}
        if len(paths_b1) == 0:
            return False
        resp = input(f"path_a: {path_a} has same md5 as path_b: {paths_b1}."
                     f" Delete?")
        if resp.strip() == 'y':
            return True
        else:
            return False

# %%


def index_path(parent_path: Path):
    index: dict[FileKey, set[Path]] = defaultdict(set)

    paths = list(parent_path.glob('**/*'))
    n_paths = len(paths)
    print(f"paths in {parent_path} has: {n_paths}")

    for i, path1 in enumerate(paths):
        name = path1.name
        size = path1.stat().st_size
        key = (name, size)
        index[key].add(path1)
        if i % 100 == 0:
            print(f"{i}/{n_paths}")

    return index
# %%


def calc_total_size(index: dict[FileKey, set[Path]]) -> int:
    total_size = 0
    for key, paths in index.items():
        total_size += key[1] * len(paths)
    return total_size


def group_by_md5(paths: set[Path]) -> dict[str, set[Path]]:
    md5_to_paths = defaultdict(set)
    for path in paths:
        if path.is_dir():
            continue
        md5_to_paths[md5(path.read_bytes()).hexdigest()].add(path)
    return md5_to_paths
# %%


def find_empty_dirs(parent_path: Path) -> list[Path]:
    empty_dirs = []
    for path in parent_path.glob('**/*'):
        if path.is_dir() and not any(path.iterdir()):
            empty_dirs.append(path)
    return empty_dirs

# %%
