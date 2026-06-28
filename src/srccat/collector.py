from pathlib import Path
from collections.abc import Iterator, Sequence
from logging import Logger
import os
import srccat.filter as filter



class FileCollector:
    _EXCLUDE_DIR = (".venv", "venv", "__pycache__", ".git")

    def __init__(
        self,
        srcdir: Path,
        filter: filter.FileFilter,
        recursive: bool,
        exclude_dirs: Sequence[str],
        logger: Logger,
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
        """
        深さ優先探索を採用
        """
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
                            self._logger.info("skip file scan: file not found: %s", entry.path)
                            continue
                        except PermissionError as ex:
                            self._logger.warning("skip file scan: %s: %s", entry.path, ex)
                            continue
            except FileNotFoundError:
                self._logger.info("skip directory scan: file not found: %s", p)
                continue
            except PermissionError as ex:
                self._logger.warning("skip directory scan: %s", p)
                continue
