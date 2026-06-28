from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
from abc import ABC, abstractmethod
from typing import override
import os


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
        scan_recursive: bool,
        exclude_dir_names: Sequence[str],
    ):
        if not scan_root_dir.is_dir():
            raise ValueError(
                f"scan tmp_path directory is not directory: {scan_root_dir}"
            )
        self._scan_root_dir = scan_root_dir
        self._scan_recursive = scan_recursive
        self._exclude_dir_names = [*exclude_dir_names, *self._EXCLUDE_DIR_NAMES]


class DFSDirectoryScanner(DirectoryScanner):
    """
    ディレクトリをDFSで検索してファイルを取得するクラスです。
    """

    def __init__(
        self,
        scan_root_dir: Path,
        scan_recursive: bool,
        exclude_dir_names: Sequence[str],
        logger: Logger,
    ):
        super().__init__(scan_root_dir, scan_recursive, exclude_dir_names)
        self._logger = logger

    @override
    def collect_files(self) -> Iterator[Path]:
        """
        深さ優先探索を採用
        """
        if self._scan_root_dir.name in self._exclude_dir_names:
            return

        dir_stack: list[Path] = [self._scan_root_dir]
        while dir_stack:
            p = dir_stack.pop()
            try:
                with os.scandir(p) as it:
                    for entry in it:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                yield Path(entry.path)
                            elif (
                                entry.is_dir(follow_symlinks=False)
                                and self._scan_recursive
                                and (entry.name not in self._exclude_dir_names)
                            ):
                                dir_stack.append(Path(entry.path))
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
