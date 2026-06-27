from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
import re
import os



class FileCollector:
    _EXCLUDE_DIR = [".venv", "venv"]

    def __init__(
        self,
        srcdir: Path,
        pattern: re.Pattern[str],
        recursive: bool,
        exclude_dirs: Sequence[str] = [],
        logger: Logger | None = None,
    ):
        self._srcdir = srcdir
        self._pattern = pattern
        self._recursive = recursive
        self._logger = logger
        self._exclude_dirs = [*self._EXCLUDE_DIR, *exclude_dirs]

    def collect_target_files(self) -> Iterator[Path]:
        for entry in self._collect_files(str(self._srcdir), self._recursive):
            if not self._pattern.match(entry.name):
                continue
            yield Path(entry.path)

    def _collect_files(
        self, srcdir: str, recursive: bool
    ) -> Iterator[os.DirEntry[str]]:
        dir_stack: list[str] = [srcdir]
        while dir_stack:
            p = dir_stack.pop()
            try:
                with os.scandir(p) as it:
                    for entry in it:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                yield entry
                            elif (
                                entry.is_dir(follow_symlinks=False)
                                and recursive
                                and (entry.name not in self._exclude_dirs)
                            ):
                                dir_stack.append(entry.path)
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


__all__ = ["FileCollector"]
