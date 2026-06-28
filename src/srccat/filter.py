from abc import ABC, abstractmethod
import re
from pathlib import Path
from typing import Sequence, override

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
    def __init__(self, filters: Sequence[FileFilter]):
        self._filters = filters

    @override
    def is_target(self, file: Path) -> bool:
        for filter in self._filters:
            if not filter.is_target(file):
                return False
        return True

