from dataclasses import dataclass
from enum import Enum
import re

import srccat.errors as errors


class Encoding(Enum):

    UTF8 = "utf-8"
    UTF16 = "utf-16"
    SHIFTJIS = "shift_jis"

    @property
    def display_name(self) -> str:
        return self.value

    @property
    def codec(self) -> str:
        return self.value

    @classmethod
    def from_str(cls, encoding_str: str) -> Encoding:
        patterns: list[tuple[re.Pattern[str], Encoding]] = [
            (re.compile(r"^utf[-_]?8$", re.IGNORECASE), Encoding.UTF8),
            (re.compile(r"^utf[-_]?16$", re.IGNORECASE), Encoding.UTF16),
            (re.compile(r"^shift[-_]?jis$", re.IGNORECASE), Encoding.SHIFTJIS),
        ]

        for pattern, encoding in patterns:
            if pattern.fullmatch(encoding_str.strip()) is not None:
                return encoding
        raise errors.InvalidArgumentError(f"unsupported encoding: {encoding_str}")


class Result(Enum):
    Success = "success"
    Fail = "fail"


@dataclass(frozen=True)
class LoadResult:
    """
    インスタンスの生成にはコンストラクタではなくsuccess/failメソッドを使用してください。
    """

    result: Result
    exception: Exception | None

    def __post_init__(self):
        if self.result == Result.Success and self.exception is not None:
            raise errors.InvalidStatusError("result is success with exception")

        if self.result == Result.Fail and self.exception is None:
            raise errors.InvalidStatusError("result is fail without exception")

    @property
    def is_success(self) -> bool:
        return self.result == Result.Success

    @classmethod
    def success(cls) -> LoadResult:
        return LoadResult(Result.Success, None)

    @classmethod
    def fail(cls, exception: Exception) -> LoadResult:
        return LoadResult(Result.Fail, exception)


@dataclass(frozen=True)
class LoadedSourceCode:
    """
    インスタンスの生成にはコンストラクタではなくwith_success/with_failメソッドを使用してください。
    """

    file_path: str
    code: str | None
    load_result: LoadResult

    def __post_init__(self):
        # パスとして有効かはパスとして使用した場合にわかるため、ここでは空の場合と巨大な文字列の場合を除外する
        path_length = len(self.file_path)
        if path_length == 0 or path_length >= 300:
            raise errors.InvalidArgumentError(
                f"path is blank or too long: {path_length}"
            )

        if self.load_result.is_success and self.code is None:
            raise errors.InvalidStatusError("load success but code is None")

        if not self.load_result.is_success and self.code is not None:
            raise errors.InvalidStatusError("load is faile but code is not None")

    @property
    def is_load_success(self) -> bool:
        return self.load_result.is_success

    @property
    def error(self) -> Exception | None:
        return self.load_result.exception

    @classmethod
    def with_success(cls, file_path: str, code: str) -> LoadedSourceCode:
        return LoadedSourceCode(file_path, code, LoadResult.success())

    @classmethod
    def with_fail(cls, file_path: str, exception: Exception) -> LoadedSourceCode:
        return LoadedSourceCode(file_path, None, LoadResult.fail(exception))


@dataclass(frozen=True)
class _LangInfo:
    display_name: str
    template_filename: str
    filename_pattern: re.Pattern[str]


class Language(Enum):
    PYTHON = _LangInfo("Python", "review_py.template", re.compile(r"^.+\.py$"))
    CSHARP = _LangInfo("C#", "review_cs.template", re.compile(r"^.+\.cs$"))
    VBNET = _LangInfo("VB.NET", "review_vb.template", re.compile(r"^.+\.vb$"))
    JAVA = _LangInfo("Java", "review_java.template", re.compile(r"^.+\.java$"))
    KOTLIN = _LangInfo("Kotlin", "review_kt.template", re.compile(r"^.+\.kt$"))

    @property
    def display_name(self) -> str:
        return self.value.display_name

    @property
    def template_filename(self) -> str:
        return self.value.template_filename

    @property
    def filename_pattern(self) -> re.Pattern[str]:
        return self.value.filename_pattern

    @classmethod
    def from_str(cls, language: str) -> Language:
        for lang in cls:
            if lang.name == language.upper():
                return lang
        raise errors.InvalidArgumentError(f"unsupported language: '{language}'")
