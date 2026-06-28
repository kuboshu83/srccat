import argparse
import re
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod

import srccat.model
import srccat.errors


@dataclass(frozen=True)
class ApplicationConfig:
    """
    外部からの取得が必要なアプリケーションで使用する設定
    """

    language: srccat.model.Language
    scan_directory_recursive: bool
    scan_root_directory: Path
    scan_exclude_directory_names: tuple[str, ...]
    source_file_encoding: srccat.model.Encoding
    source_file_name_patterns: tuple[re.Pattern[str], ...]

    @classmethod
    def convert_from(
        cls,
        programming_language: str,
        scan_directory_recursive: bool,
        scan_root_directory: str,
        scan_exclude_directory_names: list[str],
        source_file_encoding: str,
        source_file_name_patterns: list[str],
    ) -> ApplicationConfig:
        try:
            language = srccat.model.Language.from_str(programming_language)
        except ValueError as ex:
            raise srccat.errors.InvalidConfigError(
                f"invalid programming language: {programming_language}"
            ) from ex

        dirpath = Path(scan_root_directory)
        if not dirpath.is_dir():
            raise srccat.errors.InvalidConfigError(
                f"scan root directory is not directory: {scan_root_directory}"
            )

        try:
            encoding = srccat.model.Encoding.from_str(source_file_encoding)
        except ValueError as ex:
            raise srccat.errors.InvalidConfigError(
                f"invalid encoding: {source_file_encoding}"
            ) from ex

        patterns: list[re.Pattern[str]] = []
        for pattern in source_file_name_patterns:
            try:
                patterns.append(re.compile(pattern))
            except re.PatternError as ex:
                raise srccat.errors.InvalidConfigError(
                    f"invalid search file name regex pattern: {pattern}"
                ) from ex

        return ApplicationConfig(
            language=language,
            scan_directory_recursive=scan_directory_recursive,
            scan_root_directory=dirpath,
            scan_exclude_directory_names=tuple(scan_exclude_directory_names),
            source_file_encoding=encoding,
            source_file_name_patterns=tuple(patterns),
        )


class ConfigGenerator(ABC):
    """
    アプリケーションで使用する設定を取得するAPI
    """

    @abstractmethod
    def get_config(self) -> ApplicationConfig:
        pass


class CommandLineConfigGenerator(ConfigGenerator):
    """
    コマンドラインから設定を取得するクラス
    """

    def get_config(self) -> ApplicationConfig:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--language", type=str, required=True, help="taget programming language"
        )

        parser.add_argument(
            "--recursive",
            action="store_false",
            help="enable recursive directory scan mode",
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
            type=list[str],
            nargs="+",
            help="scan exclude directories",
            default=[],
        )
        parser.add_argument(
            "--patterns",
            type=list[str],
            nargs="+",
            help="collect file name patterns",
            default=[],
        )

        args = parser.parse_args()

        return ApplicationConfig.convert_from(
            programming_language=args.language,
            scan_directory_recursive=args.recursive,
            scan_root_directory=args.directory,
            scan_exclude_directory_names=args.excludes,
            source_file_encoding=args.encoding,
            source_file_name_patterns=args.patterns,
        )
