from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
from abc import ABC, abstractmethod
from typing import override
import re
import os


class FileFilter(ABC):
    @abstractmethod
    def is_target(self, file: Path) -> bool:
        pass


class FileFilterByFileNamePattern(FileFilter):
    def __init__(self, pattern: re.Pattern[str]):
        self._pattern = pattern

    @override
    def is_target(self, file: Path) -> bool:
        return self._pattern.fullmatch(file.name) is not None


class FileFilters(FileFilter):
    def __init__(self):
        self._filters: list[FileFilter] = []

    def add_filter(self, filter: FileFilter):
        self._filters.append(filter)

    @override
    def is_target(self, file: Path) -> bool:
        for filter in self._filters:
            if not filter.is_target(file):
                return False
        return True


class FileCollector:
    _EXCLUDE_DIR = (".venv", "venv", "__pycache__", ".git")

    def __init__(
        self,
        srcdir: Path,
        filter: FileFilter,
        recursive: bool,
        exclude_dirs: Sequence[str],
        logger: Logger | None = None,
    ):
        self._srcdir = srcdir
        self._filter = filter
        self._recursive = recursive
        self._logger = logger
        self._exclude_dirs = set([*self._EXCLUDE_DIR, *exclude_dirs])

    def collect_target_files(self) -> Iterator[Path]:
        for filepath in self._collect_files(self._srcdir, self._recursive):
            if not self._filter.is_target(filepath):
                continue
            yield filepath

    def _collect_files(self, srcdir: Path, recursive: bool) -> Iterator[Path]:
        dir_stack: list[Path] = [srcdir]
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
                                and recursive
                                and (entry.name not in self._exclude_dirs)
                            ):
                                dir_stack.append(Path(entry.path))
                        except FileNotFoundError:
                            self._log_info(
                                f"skip file scan: file not found: {entry.path}"
                            )
                            continue
                        except PermissionError as ex:
                            self._log_warning(f"skip file scan: {entry.path}", ex)
                            continue
            except FileNotFoundError:
                self._log_info(f"skip directory scan: file not found: {p}")
                continue
            except PermissionError as ex:
                self._log_warning(f"skip directory scan: {p}", ex)
                continue

    def _log_info(self, msg: str):
        if self._logger is not None:
            self._logger.info(msg)

    def _log_warning(self, msg: str, ex: Exception):
        if self._logger is not None:
            self._logger.warning("%s: %s", msg, ex, exc_info=True)


__all__ = ["FileCollector", "FileFilter", "FileFilters"]
