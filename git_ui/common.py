import os
# Selection mapping: 1-9, then a-z
SELECTION_CHARS = "123456789abcdefghijklmnopqrstuvwxyz"


def find_git_root() -> str | None:
    """Traverse upwards to find the .git directory."""
    curr = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(curr, ".git")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:  # Reached root
            return None
        curr = parent
