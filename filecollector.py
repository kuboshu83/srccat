from pathlib import Path
from collections.abc import Iterator
import re
import os

EXCLUDE_DIR = [".venv", "venv"]


def search_srcfiles(
    srcdir: Path, pattern: re.Pattern[str], recursive: bool
) -> Iterator[Path]:
    for entry in _scan_dir(str(srcdir), recursive):
        if not entry.is_file():
            continue
        if not pattern.match(entry.name):
            continue
        yield Path(entry.path)


def _scan_dir(srcdir: str, recursive: bool) -> Iterator[os.DirEntry[str]]:
    dir_stack: list[str] = [srcdir]
    while dir_stack:
        try:
            p = dir_stack.pop()
            with os.scandir(p) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            yield entry
                        elif (
                            entry.is_dir(follow_symlinks=False)
                            and recursive
                            and (entry.name not in EXCLUDE_DIR)
                        ):
                            dir_stack.append(entry.path)
                    except FileNotFoundError, PermissionError:
                        continue
        except FileNotFoundError, PermissionError:
            continue


__all__ = ["search_srcfiles"]
