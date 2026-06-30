from abc import ABC, abstractmethod
import re
from pathlib import Path
from typing import Sequence, override

import srccat.model as model


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
        """
        フィルター未登録状態では常にTrueを返すので注意してください。
        """
        # 登録フィルタがない場合は、そもそもフィルタリングしないことと同意なので常にTrueを返す
        if len(self._filters) == 0:
            return True

        for filter in self._filters:
            if filter.is_target(file):
                return True
        return False


def create_file_name_filter(
    file_name_patterns: Sequence[re.Pattern[str]],
) -> FileFilter:
    """
    パターンが１つも渡されなかったら、名前でフィルタしないことになるので常にTrueを返すフィルタを作成する。
    """
    # ファイル名は様々なパターンで取得したくなる場合が多いので、ANDではなくてORで結合するのが無難。
    file_name_filters: list[FileNameFilter] = []
    for pattern in file_name_patterns:
        file_name_filters.append(FileNameFilter(pattern))
    return FileFilterOrCondition(file_name_filters)


# 対応言語が増えた場合はここに要素を追加してください。
# プログラム内からの更新はしないでください。
_FILE_FILTERS: dict[model.Language, Sequence[FileFilter]] = {
    model.Language.PYTHON: tuple(
        [
            FileNameFilter(
                model.get_language_default_filename_pattern(model.Language.PYTHON)
            ),
        ]
    ),
    model.Language.CSHARP: tuple(
        [
            FileNameFilter(
                model.get_language_default_filename_pattern(model.Language.CSHARP)
            ),
        ]
    ),
    model.Language.VBNET: tuple(
        [
            FileNameFilter(
                model.get_language_default_filename_pattern(model.Language.VBNET)
            ),
        ]
    ),
    model.Language.JAVA: tuple(
        [
            FileNameFilter(
                model.get_language_default_filename_pattern(model.Language.JAVA)
            ),
        ]
    ),
    model.Language.KOTLIN: tuple(
        [
            FileNameFilter(
                model.get_language_default_filename_pattern(model.Language.KOTLIN)
            ),
        ]
    ),
}


def build_filename_fileter(
    language: model.Language, additional_patterns: Sequence[re.Pattern[str]]
) -> FileFilter:
    """
    言語毎のデフォルトのファイル名パターンとユーザ定義のファイル名パターンを合成したフィルタを生成します。
    いずれかのパターンに一致するファイルを透過させるフィルタとなります。
    """
    default_pattern = model.get_language_default_filename_pattern(language)
    patterns = [default_pattern, *additional_patterns]

    filters: list[FileNameFilter] = []
    for pattern in patterns:
        filters.append(FileNameFilter(pattern))

    return FileFilterOrCondition(filters)
