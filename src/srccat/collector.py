from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
from abc import ABC, abstractmethod
from typing import override
import re
import os

import srccat.errors as errors
import srccat.filefilter as filefilter

# 常に検索から除外したいディレクトリはここに追加してください
_DEFAULT_EXCLUDE_DIR_NAME_PATTERNS = (
    re.compile(r"^\.venv$"),
    re.compile(r"^venv$"),
    re.compile(r"^__pycache__$"),
    re.compile(r"^\.git$"),
)


class DirectoryRejector(ABC):
    """
    ディレクトリを検索対象から除外するためのフィルタ
    """

    @abstractmethod
    def is_reject_target(self, dir_path: Path) -> bool:
        pass


class AllRejector(DirectoryRejector):
    """
    全てのディレクトリをブロックするフィルタです。
    再帰的なディレクトリ検索を無効化する場合に使用します。
    """

    @override
    def is_reject_target(self, dir_path: Path) -> bool:
        return True


class DirectoryNameRejectFilter(DirectoryRejector):
    """
    ディレクトリ名から除外対象を判定するフィルタ
    """

    def __init__(self, directory_name_pattern: re.Pattern[str]):
        self._directory_name_pattern = directory_name_pattern

    @override
    def is_reject_target(self, dir_path: Path) -> bool:
        return self._directory_name_pattern.fullmatch(dir_path.name) is not None


class DirectoryRejectorOrCondition(DirectoryRejector):
    def __init__(self, filters: Sequence[DirectoryRejector]):
        self._filters = filters

    @override
    def is_reject_target(self, dir_path: Path) -> bool:
        # 登録Rejectorがない場合は、そもそもRejectしないことと同意なので常にFalseを返す
        if len(self._filters) == 0:
            return False

        for filter in self._filters:
            if filter.is_reject_target(dir_path):
                return True
        return False


def create_scan_directory_reject_filter(
    is_recursive: bool,
    additional_reject_dir_name_patterns: Sequence[re.Pattern[str]],
) -> DirectoryRejector:
    directory_rejector: list[DirectoryRejector] = []

    if not is_recursive:
        directory_rejector.append(AllRejector())

    for pattern in _DEFAULT_EXCLUDE_DIR_NAME_PATTERNS:
        directory_rejector.append(DirectoryNameRejectFilter(pattern))

    for pattern in additional_reject_dir_name_patterns:
        directory_rejector.append(DirectoryNameRejectFilter(pattern))

    # 1つでもReject条件にマッチしたらRejectになるためOrで結合する
    return DirectoryRejectorOrCondition(directory_rejector)


class DirectoryScanner(ABC):
    """
    ディレクトリを検索してファイルを収集するAPI
    検索途中でエラーが発生した場合は、そのファイル/ディレクトリの検索をスキップします。
    そして、エラーカウントを+1してから他のファイル/ディレクトリの検索を続けます。
    """

    def __init__(
        self,
        scan_root_dir: Path,
        directory_rejector: DirectoryRejector,
    ):
        if not scan_root_dir.is_dir():
            raise errors.InvalidArgumentError(
                f"scan tmp_path directory is not directory: {scan_root_dir}"
            )
        self._scan_root_dir = scan_root_dir
        self._directory_rejector = directory_rejector
        self._error_count = 0

    @property
    def error_count(self) -> int:
        return self._error_count

    def _reset_error_count(self):
        self._error_count = 0

    @abstractmethod
    def collect_files(self) -> Iterator[Path]:
        """
        このメソッドの最初で必ず_reset_error_countを実行してください。
        """
        pass


class DFSDirectoryScanner(DirectoryScanner):
    """
    ディレクトリをDFSで検索してファイルを取得するクラスです。
    """

    def __init__(
        self,
        scan_root_dir: Path,
        directory_rejector: DirectoryRejector,
        logger: Logger,
    ):
        super().__init__(scan_root_dir, directory_rejector)
        self._logger = logger

    def _info_log_with_error(self, msg: str, ex: Exception):
        self._error_count += 1
        self._logger.info("%s: %s", msg, ex)

    def _warning_log_with_error(self, msg: str, ex: Exception):
        self._error_count += 1
        self._logger.warning("%s: %s", msg, ex)

    @override
    def collect_files(self) -> Iterator[Path]:
        """
        深さ優先探索を採用
        """

        self._reset_error_count()

        dir_stack: list[Path] = [self._scan_root_dir]
        while dir_stack:
            p = dir_stack.pop()
            try:
                with os.scandir(p) as it:
                    for entry in it:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                yield Path(entry.path)
                            elif entry.is_dir(follow_symlinks=False):
                                dir_path = Path(entry.path)
                                if not self._directory_rejector.is_reject_target(
                                    dir_path
                                ):
                                    dir_stack.append(dir_path)
                        except FileNotFoundError as ex:
                            self._info_log_with_error(
                                f"skip file scan: file not found: {entry.path}", ex
                            )
                            continue
                        except PermissionError as ex:
                            self._warning_log_with_error(
                                "skip file scan: permission error :{entry.path}", ex
                            )
                            continue
            except FileNotFoundError as ex:
                self._info_log_with_error(
                    "skip directory scan: directory not found: {p}", ex
                )
                continue
            except PermissionError as ex:
                self._warning_log_with_error(
                    "skip directory scan: permission error: {p}", ex
                )
                continue


class FilteredFileCollector:

    def __init__(
        self,
        file_collector: DirectoryScanner,
        file_filter: filefilter.FileFilter,
    ):
        self._file_collector = file_collector
        self._file_filter = file_filter

    @property
    def error_count(self) -> int:
        """
        ファイル収集の際に発生したエラー数。
        collect_target_filesメソッドを呼び出すたびに0にリセットされます。
        """
        return self._file_collector.error_count

    def collect_target_files(self) -> Iterator[Path]:
        for file_path in self._file_collector.collect_files():
            if not self._file_filter.is_target(file_path):
                continue
            yield file_path
