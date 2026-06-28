from abc import ABC, abstractmethod
import re
from pathlib import Path
from typing import Sequence, override, Iterator
import srccat.collector


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


class AndFileFilters(FileFilter):
    """
    複数のフィルタをandで合成するクラス。
    """

    def __init__(self, filters: Sequence[FileFilter]):
        self._filters = filters

    @override
    def is_target(self, file: Path) -> bool:
        """
        フィルタが１つも登録されていない場合は常にTrueを返します
        """
        for filter in self._filters:
            if not filter.is_target(file):
                return False
        return True


class FilteredFileCollector:

    def __init__(
        self,
        file_collector: srccat.collector.FileCollector,
        file_filter: FileFilter,
    ):
        self._file_collector = file_collector
        self._file_filter = file_filter

    def collect_target_files(self) -> Iterator[Path]:
        for filepath in self._file_collector.collect_files():
            if not self._file_filter.is_target(filepath):
                continue
            yield filepath


