from pathlib import Path
import re

import srccat.model as model
import srccat.render as render
import srccat.collector as collector
import logging


def run(language: model.Language, collector: collector.FileCollector):
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


def main():
    language = model.Language.from_str("Python")
    srcdir = Path(".")
    filters = collector.AndFileFilters(
        [collector.FileFilterByFileNamePattern(re.compile(r"^.+\.py$"))]
    )
    logger = logging.getLogger("srccat")
    file_collector = collector.FileCollector(srcdir, filters, True, [], logger)
    run(language, file_collector)


if __name__ == "__main__":
    main()
