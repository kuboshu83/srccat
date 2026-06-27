from collections.abc import Iterator
from typing import Callable
from pathlib import Path
import os
import re

import model
import render

EXCLUDE_DIR = [".venv", "venv"]


def main(language: str, srcdir: Path, pattern: re.Pattern[str], recursive: bool):
    text = cat_srcfiles(language, srcdir, pattern, recursive, _search_srcfiles)
    print(text)


def cat_srcfiles(
    language: str,
    srcdir: Path,
    pattern: re.Pattern[str],
    recursive: bool,
    collect_files: Callable[[Path, re.Pattern[str], bool], Iterator[Path]],
) -> str:
    lang = render.Language.from_str(language)
    srcfiles: list[model.SrcFile] = []
    for path in collect_files(srcdir, pattern, recursive):
        srcfiles.append(
            model.SrcFile(str(path), path.read_text(encoding="utf-8", errors="strict"))
        )
    return render.render_review_document(lang, srcfiles)
    # return _cat_srcfiles(header, srcfiles)


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


if __name__ == "__main__":
    language = render.Language.from_str("Python")
    srcdir = Path(".")
    pattern = re.compile(r"^.+\.py$")
    main(language.value.display_name, srcdir, pattern, True)
