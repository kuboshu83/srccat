import srccat.model
import srccat.render
import srccat.collector
import srccat.filefilter
import srccat.config
import srccat.processor as processor
import logging

# ソースコードの最大の行番号。10000行あるコードはレビュー以前にNGなので10000に設定する。
_MAX_LINE_NO = 10000


def run(
    language: srccat.model.Language,
    collector: srccat.collector.FilteredFileCollector,
    encoding: srccat.model.Encoding,
    max_source_file_line_no: int,
) -> str:
    return build_review_document(language, collector, encoding, max_source_file_line_no)


def build_review_document(
    language: srccat.model.Language,
    collector: srccat.collector.FilteredFileCollector,
    encoding: srccat.model.Encoding,
    max_source_file_line_no: int,
) -> str:
    loaded_source_files: list[srccat.model.LoadedSourceCode] = []
    for path in collector.collect_target_files():
        try:
            code_body = processor.add_line_number_to_head(
                path.read_text(encoding=encoding.codec, errors="strict"),
                max_source_file_line_no,
            )
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
        + (srccat.model.get_language_default_filename_pattern(language),)
    )
    logger = logging.getLogger("srccat")
    scan_directory_filter = srccat.collector.create_scan_directory_reject_filter(
        is_recursive=config.scan_directory_recursive,
        additional_reject_dir_name_patterns=config.reject_dir_name_patterns,
    )
    dir_scanner = srccat.collector.DFSDirectoryScanner(
        scan_root_dir=scan_root_dir,
        directory_rejector=scan_directory_filter,
        logger=logger,
    )
    file_collector = srccat.collector.FilteredFileCollector(dir_scanner, filters)
    encoding = config.source_file_encoding
    text = run(language, file_collector, encoding, _MAX_LINE_NO)
    print(text)

    error_count = file_collector.error_count
    if error_count != 0:
        logger.warning(f"{error_count} errors occurred while collecting files.")


if __name__ == "__main__":
    main()
