from pathlib import Path
import re

import model
import render
import collector


def main(language: model.Language, collector: collector.FileCollector):
    text = build_review_document(language, collector)
    print(text)


def build_review_document(
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
    filters = collector.FileFilters()
    filters.add_filter(collector.FileFilterByFileNamePattern(re.compile(r"^.+\.py$")))
    file_collector = collector.FileCollector(srcdir, filters, True, [], None)
    main(language, file_collector)
