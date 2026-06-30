import srccat.model as model
import srccat.render as render
import srccat.collector as collector
import srccat.filefilter as filefilter
import srccat.config as config
import srccat.processor as processor
import logging

# ソースコードの最大の行番号。10000行あるコードはレビュー以前にNGなので10000に設定する。
_MAX_LINE_NO = 10000


def run(
    language: model.Language,
    collector: collector.FilteredFileCollector,
    encoding: model.Encoding,
    max_source_file_line_no: int,
    enable_base64: bool,
) -> str:
    text = build_review_document(language, collector, encoding, max_source_file_line_no)
    if enable_base64:
        return processor.convert_to_base64(text)
    return text


def build_review_document(
    language: model.Language,
    collector: collector.FilteredFileCollector,
    encoding: model.Encoding,
    max_source_file_line_no: int,
) -> str:
    loaded_source_files: list[model.LoadedSourceCode] = []
    code_processor = processor.build_source_code_processor(
        max_source_file_line_no, language
    )
    for path in collector.collect_target_files():
        try:
            raw_code = path.read_text(encoding=encoding.codec, errors="strict")
            processed_code = code_processor(raw_code)
            loaded_source_files.append(
                model.LoadedSourceCode.with_success(str(path), processed_code)
            )
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as ex:
            loaded_source_files.append(model.LoadedSourceCode.with_fail(str(path), ex))
    return render.render_review_document(language, loaded_source_files)


def main():
    app_config = config.CommandLineConfigGenerator().get_config()
    language = app_config.language
    scan_root_dir = app_config.scan_root_directory
    filters = filefilter.create_file_name_filter(
        file_name_patterns=app_config.source_file_name_patterns
        + (model.get_language_default_filename_pattern(language),)
    )
    logger = logging.getLogger("srccat")
    scan_directory_filter = collector.create_scan_directory_reject_filter(
        is_recursive=app_config.scan_directory_recursive,
        additional_reject_dir_name_patterns=app_config.reject_dir_name_patterns,
    )
    dir_scanner = collector.DFSDirectoryScanner(
        scan_root_dir=scan_root_dir,
        directory_rejector=scan_directory_filter,
        logger=logger,
    )
    file_collector = collector.FilteredFileCollector(dir_scanner, filters)
    encoding = app_config.source_file_encoding
    base64 = app_config.enable_encode_base64
    text = run(language, file_collector, encoding, _MAX_LINE_NO, base64)
    print(text)

    error_count = file_collector.error_count
    if error_count != 0:
        logger.warning(f"{error_count} errors occurred while collecting files.")


if __name__ == "__main__":
    main()
