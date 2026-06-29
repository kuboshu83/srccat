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
    loaded_source_files: list[srccat.model.LoadedSourceCode] = []
    for path in collector.collect_target_files():
        try:
            code_body = path.read_text(encoding=encoding.codec, errors="strict")
            loaded_source_files.append(
                srccat.model.LoadedSourceCode.with_success(str(path), code_body)
            )
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as ex:
            loaded_source_files.append(
                srccat.model.LoadedSourceCode.with_fail(str(path), ex)
            )
    return srccat.render.render_review_document(language, loaded_source_files)


def main():
    config = srccat.config.CommandLineConfigGenerator().get_config()
    language = config.language
    scan_root_dir = config.scan_root_directory
    filters = srccat.filefilter.create_file_name_filter(
        file_name_patterns=config.source_file_name_patterns
        + (language.filename_pattern,)
    )
    logger = logging.getLogger("srccat")
    scan_directory_filter = srccat.collector.create_scan_directory_reject_filter(
        is_recursive=config.scan_directory_recursive,
        additional_reject_dir_name_patterns=config.reject_dir_name_patterns,
    )
    file_collector = srccat.collector.DFSDirectoryScanner(
        scan_root_dir=scan_root_dir,
        directory_rejector=scan_directory_filter,
        logger=logger,
    )
    file_collector = srccat.filefilter.FilteredFileCollector(file_collector, filters)
    encoding = config.source_file_encoding
    run(language, file_collector, encoding)


if __name__ == "__main__":
    main()
