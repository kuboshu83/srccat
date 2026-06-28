from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
from abc import ABC, abstractmethod
from typing import override
import os


class DirectoryScanPolicy(ABC):
    """
    ディレクトリを検索する際の検索対象かどうかの判定基準
    """

    @abstractmethod
    def is_scantarget(self, dirpath: Path) -> bool:
        pass


class DisableScanDirectoryPolicy(DirectoryScanPolicy):
    """
    全てのディレクトリの検索を無効にしたい場合のポリシー
    """
    @override
    def is_scantarget(self, dirpath: Path) -> bool:
        """
        常にFalseを返します。
        """
        return False


class DirectoryNameScanPolicy(DirectoryScanPolicy):
    """
    ディレクトリを検索するかをディレクトリ名から判定する条件
    """

    _EXCLUDE_DIR_NAMES = (".venv", "venv", "__pycache__", ".git")

    def __init__(self, exclude_dir_names: Sequence[str]):
        self._exclude_dir_names = [*self._EXCLUDE_DIR_NAMES, *exclude_dir_names]

    @override
    def is_scantarget(self, dirpath: Path) -> bool:
        return dirpath.name not in self._exclude_dir_names


class AndDirectoryScanPolicies(DirectoryScanPolicy):
    """
    登録されたディレクトリ検索条件が全て満たされているかを判定するための条件
    """

    def __init__(self, scan_policies: Sequence[DirectoryScanPolicy]):
        self._scan_policies = tuple(scan_policies)

    @override
    def is_scantarget(self, dirpath: Path) -> bool:
        """
        条件が未登録の場合は常にTrueを返します。
        """
        for policy in self._scan_policies:
            if not policy.is_scantarget(dirpath):
                return False
        return True


class FileCollector(ABC):
    """
    ファイル収集するAPI
    """

    @abstractmethod
    def collect_files(self) -> Iterator[Path]:
        pass


class DirectoryScanner(FileCollector):
    """
    ディレクトリを検索してファイルを収集するAPI
    """

    _EXCLUDE_DIR_NAMES = (".venv", "venv", "__pycache__", ".git")

    def __init__(
        self,
        scan_root_dir: Path,
        directory_scan_policy: DirectoryScanPolicy,
    ):
        if not scan_root_dir.is_dir():
            raise ValueError(
                f"scan tmp_path directory is not directory: {scan_root_dir}"
            )
        self._scan_root_dir = scan_root_dir
        self._directory_scan_policy = directory_scan_policy


class DFSDirectoryScanner(DirectoryScanner):
    """
    ディレクトリをDFSで検索してファイルを取得するクラスです。
    """

    def __init__(
        self,
        scan_root_dir: Path,
        directory_scan_policy: DirectoryScanPolicy,
        logger: Logger,
    ):
        super().__init__(scan_root_dir, directory_scan_policy)
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
                                dir = Path(entry)
                                if self._directory_scan_policy.is_scantarget(dir):
                                    dir_stack.append(dir)
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
