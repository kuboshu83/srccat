from pathlib import Path
import re

import model
import render
import collector


def main(language: model.Language, collector: collector.FileCollector):
    text = cat_srcfiles(language, collector)
    print(text)


def cat_srcfiles(
    language: model.Language,
    collector: collector.FileCollector,
) -> str:
    srcfiles: list[model.SrcFile] = []
    for path in collector.collect_target_files():
        srcfiles.append(
            model.SrcFile(str(path), path.read_text(encoding="utf-8", errors="strict"))
        )
    return render.render_review_document(language, srcfiles)


if __name__ == "__main__":
    language = model.Language.from_str("Python")
    srcdir = Path(".")
    pattern = re.compile(r"^.+\.py$")
    file_collector = collector.FileCollector(srcdir, pattern, True, [], None)
    main(language, file_collector)
