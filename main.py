from collections.abc import Iterator
from typing import Callable
from pathlib import Path
import re

import model
import render
import filecollector


def main(language: str, srcdir: Path, pattern: re.Pattern[str], recursive: bool):
    text = cat_srcfiles(
        language, srcdir, pattern, recursive, filecollector.search_srcfiles
    )
    print(text)


def cat_srcfiles(
    language: str,
    srcdir: Path,
    pattern: re.Pattern[str],
    recursive: bool,
    collect_files: Callable[[Path, re.Pattern[str], bool], Iterator[Path]],
) -> str:
    lang = model.Language.from_str(language)
    srcfiles: list[model.SrcFile] = []
    for path in collect_files(srcdir, pattern, recursive):
        srcfiles.append(
            model.SrcFile(str(path), path.read_text(encoding="utf-8", errors="strict"))
        )
    return render.render_review_document(lang, srcfiles)


if __name__ == "__main__":
    language = model.Language.from_str("Python")
    srcdir = Path(".")
    pattern = re.compile(r"^.+\.py$")
    main(language.value.display_name, srcdir, pattern, True)
