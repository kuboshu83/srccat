from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
from abc import ABC, abstractmethod
from typing import override
import re
import os

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
    """

    def __init__(
        self,
        scan_root_dir: Path,
        directory_rejector: DirectoryRejector,
    ):
        if not scan_root_dir.is_dir():
            raise ValueError(
                f"scan tmp_path directory is not directory: {scan_root_dir}"
            )
        self._scan_root_dir = scan_root_dir
        self._directory_rejector = directory_rejector

    @abstractmethod
    def collect_files(self) -> Iterator[Path]:
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

    @override
    def collect_files(self) -> Iterator[Path]:
        """
        深さ優先探索を採用
        """
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
                        except FileNotFoundError:
                            self._logger.info(
                                "skip file scan: file not found: %s", entry.path
                            )
                            continue
                        except PermissionError as ex:
                            self._logger.warning(
                                "skip file scan: %s: %s", entry.path, ex
                            )
                            continue
            except FileNotFoundError:
                self._logger.info("skip directory scan: file not found: %s", p)
                continue
            except PermissionError as ex:
                self._logger.warning("skip directory scan: %s", p)
                continue
