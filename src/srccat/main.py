import srccat.model
import srccat.render
import srccat.collector
import srccat.filefilter
import srccat.config
import logging


def run(
    language: srccat.model.Language,
    collector: srccat.filefilter.FilteredFileCollector,
    encoding: srccat.model.Encoding,
):
    text = build_review_document(language, collector, encoding)
    print(text)


def build_review_document(
    language: srccat.model.Language,
    collector: srccat.filefilter.FilteredFileCollector,
    encoding: srccat.model.Encoding,
) -> str:
    srcfiles: list[srccat.model.SrcFile] = []
    for path in collector.collect_target_files():
        srcfiles.append(
            srccat.model.SrcFile(
                str(path), path.read_text(encoding=encoding.codec, errors="strict")
            )
        )
    return srccat.render.render_review_document(language, srcfiles)


def main():
    config = srccat.config.CommandLineConfigGenerator().get_config()
    language = config.language
    scan_root_dir = config.scan_root_directory
    filters = srccat.filefilter.create_and_file_filters(
        filename_patterns=config.source_file_name_patterns
        + (language.filename_pattern,)
    )
    logger = logging.getLogger("srccat")
    directory_scan_policy = srccat.collector.create_and_directory_scan_policy(
        recursive=config.scan_directory_recursive,
        exclude_dirnames=config.scan_exclude_directory_names,
    )
    file_collector = srccat.collector.DFSDirectoryScanner(
        scan_root_dir=scan_root_dir,
        directory_scan_policy=directory_scan_policy,
        logger=logger,
    )
    file_collector = srccat.filefilter.FilteredFileCollector(file_collector, filters)
    encoding = config.source_file_encoding
    run(language, file_collector, encoding)


if __name__ == "__main__":
    main()
