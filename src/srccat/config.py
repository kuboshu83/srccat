import argparse
import re
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Sequence

import srccat.model as model
import srccat.errors as errors


def _convert_string_to_scan_root_dir(dir_path: str) -> Path:
    path = Path(dir_path)
    if not path.is_dir():
        raise errors.InvalidConfigError(
            f"scan root directory is not directory: {dir_path}"
        )
    return path


def _convert_string_to_language(language_str: str) -> model.Language:
    try:
        return model.Language.from_str(language_str)
    except errors.InvalidArgumentError as ex:
        raise errors.InvalidConfigError(f"language conversion error: {ex}") from ex


def _convert_string_to_encoding(encoding_str: str) -> model.Encoding:
    try:
        return model.Encoding.from_str(encoding_str)
    except errors.InvalidArgumentError as ex:
        raise errors.InvalidConfigError(f"encoding conversion error: {ex}") from ex


def _convert_string_to_regex_pattern(
    pattern_strings: Sequence[str],
) -> Sequence[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []

    for pattern_str in pattern_strings:
        try:
            patterns.append(re.compile(pattern_str))
        except re.error as ex:
            raise errors.InvalidConfigError(
                f"invalid reject directory name regex pattern: {pattern_str}: {ex}"
            ) from ex
    return patterns


@dataclass(frozen=True)
class ApplicationConfig:
    """
    外部からの取得が必要なアプリケーションで使用する設定
    """

    language: model.Language
    scan_directory_recursive: bool
    scan_root_directory: Path
    reject_dir_name_patterns: tuple[re.Pattern[str], ...]
    source_file_encoding: model.Encoding
    source_file_name_patterns: tuple[re.Pattern[str], ...]

    @classmethod
    def convert_from(
        cls,
        programming_language: str,
        scan_directory_recursive: bool,
        scan_root_directory: str,
        reject_dir_name_patterns: list[str],
        source_file_encoding: str,
        source_file_name_patterns: list[str],
    ) -> ApplicationConfig:
        language = _convert_string_to_language(programming_language)
        dirpath = _convert_string_to_scan_root_dir(scan_root_directory)
        encoding = _convert_string_to_encoding(source_file_encoding)
        dir_name_patterns = _convert_string_to_regex_pattern(reject_dir_name_patterns)
        file_name_patterns = _convert_string_to_regex_pattern(source_file_name_patterns)

        return ApplicationConfig(
            language=language,
            scan_directory_recursive=scan_directory_recursive,
            scan_root_directory=dirpath,
            reject_dir_name_patterns=tuple(dir_name_patterns),
            source_file_encoding=encoding,
            source_file_name_patterns=tuple(file_name_patterns),
        )


class CommandLineConfigGenerator:
    def get_config(self) -> ApplicationConfig:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--language", type=str, required=True, help="taget programming language"
        )

        parser.add_argument(
            "--norecursive",
            action="store_true",
            help="disable recursive directory scan mode",
        )
        parser.add_argument("--directory", default=".", help="scan root directory")
        parser.add_argument(
            "--encoding",
            choices=["utf8", "utf16", "shiftjis"],
            default="utf8",
            type=str,
            help="source code file encoding",
        )
        parser.add_argument(
            "--excludes",
            type=str,
            nargs="+",
            help="scan exclude directories",
            default=[],
        )
        parser.add_argument(
            "--patterns",
            type=str,
            nargs="+",
            help="collect file name patterns",
            default=[],
        )

        args = parser.parse_args()

        recursive = not args.norecursive

        return ApplicationConfig.convert_from(
            programming_language=args.language,
            scan_directory_recursive=recursive,
            scan_root_directory=args.directory,
            reject_dir_name_patterns=args.excludes,
            source_file_encoding=args.encoding,
            source_file_name_patterns=args.patterns,
        )
