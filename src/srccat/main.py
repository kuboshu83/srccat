from pathlib import Path
import re

import srccat.model
import srccat.render
import srccat.collector
import srccat.filefilter
import logging


def run(
    language: srccat.model.Language, collector: srccat.filefilter.FilteredFileCollector
):
    text = build_review_document(language, collector)
    print(text)


def build_review_document(
    language: srccat.model.Language,
    collector: srccat.filefilter.FilteredFileCollector,
) -> str:
    srcfiles: list[srccat.model.SrcFile] = []
    for path in collector.collect_target_files():
        srcfiles.append(
            srccat.model.SrcFile(
                str(path), path.read_text(encoding="utf-8", errors="strict")
            )
        )
    return srccat.render.render_review_document(language, srcfiles)


def main():
    language = srccat.model.Language.from_str("Python")
    srcdir = Path(".")
    filters = srccat.filefilter.AndFileFilters(
        [srccat.filefilter.FileFilterByFileNamePattern(re.compile(r"^.+\.py$"))]
    )
    logger = logging.getLogger("srccat")
    scan_directory_policy = srccat.collector.AndDirectoryScanPolicies((
        # srccat.collector.DisableScanDirectoryPolicy(),
        srccat.collector.DirectoryNameScanPolicy(()),
    ))
    file_collector = srccat.collector.DFSDirectoryScanner(srcdir, scan_directory_policy, logger)
    file_collector = srccat.filefilter.FilteredFileCollector(file_collector, filters)
    run(language, file_collector)


if __name__ == "__main__":
    main()
