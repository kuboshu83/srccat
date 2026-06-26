from collections.abc import Iterator, Sequence
from typing import Callable
from pathlib import Path
from dataclasses import dataclass
import os
import re

EXCLUDE_DIR = [".venv", "venv"]


@dataclass(frozen=True)
class SrcFile:
    filepath: str
    code: str

    def __post_init__(self):
        if self.filepath == "":
            raise ValueError("file name is blank")
        if self.code == "":
            raise ValueError(f"code is blank: {self.filepath}")


@dataclass(frozen=True)
class Header:
    language: str
    language_version: str | None = None


def _cat_srcfiles(header: Header, files: Sequence[SrcFile]) -> str:
    header_block = _create_header_block(header)
    filelist_block = _create_filelist_block(files)
    code_block = _create_code_blocks(files)
    return f"""
{header_block}

{filelist_block}

{code_block}
"""


def _create_header_block(header: Header) -> str:
    return f"""
++++ 言語情報
language={header.language}
version={header.language_version}
"""


def _create_filelist_block(files: Sequence[SrcFile]) -> str:
    lines: list[str] = ["++++ ファイル一覧"]
    for path in files:
        lines.append(f"filepath={path.filepath}")
    return "\n".join(lines)


def _create_code_blocks(files: Sequence[SrcFile]) -> str:
    blocks: list[str] = []
    for file in files:
        block = _create_file_block(file)
        blocks.append(block)
    return "\n".join(blocks)


def _create_file_block(file: SrcFile) -> str:
    return f"""
++++ ソースコード情報
filepath={file.filepath}
code=```
{file.code}
```
"""


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
    header = Header(language)
    srcfiles: list[SrcFile] = []
    for path in collect_files(srcdir, pattern, recursive):
        srcfiles.append(
            SrcFile(str(path), path.read_text(encoding="utf-8", errors="strict"))
        )
    return _cat_srcfiles(header, srcfiles)


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
    language = "Python 3.14.2"
    srcdir = Path(".")
    pattern = re.compile(r"^.+\.py$")
    main(language, srcdir, pattern, True)
