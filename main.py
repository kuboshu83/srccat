from collections.abc import Iterator
from typing import Callable
from pathlib import Path
import os
import re

EXCLUDE_DIR = [".venv"]


def main(language: str, srcdir: Path, pattern: re.Pattern[str], recursive: bool):
    text = _cat_srcfiles(language, srcdir, pattern, recursive, _search_srcfiles)
    print(text)


def _cat_srcfiles(
    language: str,
    srcdir: Path,
    pattern: re.Pattern[str],
    recursive: bool,
    collect_files: Callable[[Path, re.Pattern[str], bool], Iterator[Path]],
) -> str:
    lines: list[str] = []
    lines.append(_create_language_info_block(language))
    for srcfile in collect_files(srcdir, pattern, recursive):
        srcfile_block = _create_srcfile_block(srcfile)
        lines.append(srcfile_block)
    return "\n".join(lines)


def _search_srcfiles(
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
                    except (FileNotFoundError, PermissionError):
                        continue
        except (FileNotFoundError, PermissionError):
            continue


def _create_language_info_block(language: str) -> str:
    return f"""
++++ 使用する言語の情報 ++++
language: {language}

"""


def _create_srcfile_block(src: Path) -> str:
    abs_path = src.resolve()
    src_code = src.read_text()
    return f"""
++++ ソースコード情報
filepath = {abs_path}
code = ```
{src_code}
```
"""


if __name__ == "__main__":
    language = "Python 3.14.2"
    srcdir = Path(".")
    pattern = re.compile(r"^.+\.py$")
    main(language, srcdir, pattern, True)
