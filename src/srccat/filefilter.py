from abc import ABC, abstractmethod
import re
from pathlib import Path
from typing import Sequence, override, Iterator
import srccat.collector


class FileFilter(ABC):
    @abstractmethod
    def is_target(self, file: Path) -> bool:
        pass


class FileNameFilter(FileFilter):
    def __init__(self, pattern: re.Pattern[str]):
        self._pattern = pattern

    @override
    def is_target(self, file: Path) -> bool:
        return self._pattern.fullmatch(file.name) is not None


class FileFilterOrCondition(FileFilter):
    def __init__(self, filters: Sequence[FileFilter]):
        self._filters = filters

    def is_target(self, file: Path) -> bool:
        # 登録フィルタがない場合は、そもそもフィルタリングしないことと同意なので常にTrueを返す
        if len(self._filters) == 0:
            return True

        for filter in self._filters:
            if filter.is_target(file):
                return True
        return False


def create_file_name_filter(file_name_patterns: Sequence[re.Pattern[str]]) -> FileFilter:
    # ファイル名は様々なパターンで取得したくなる場合が多いので、ANDではなくてORで結合するのが無難。
    file_name_filters: list[FileNameFilter] = []
    for pattern in file_name_patterns:
        file_name_filters.append(FileNameFilter(pattern))
    return FileFilterOrCondition(file_name_filters)


class FilteredFileCollector:

    def __init__(
        self,
        file_collector: srccat.collector.DirectoryScanner,
        file_filter: FileFilter,
    ):
        self._file_collector = file_collector
        self._file_filter = file_filter

    def collect_target_files(self) -> Iterator[Path]:
        for filepath in self._file_collector.collect_files():
            if not self._file_filter.is_target(filepath):
                continue
            yield filepath
