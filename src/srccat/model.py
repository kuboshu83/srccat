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
        # encodingの種類が増えた際はこのリストに要素を追加してください。
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
        if self.file_path.strip() == "":
            raise errors.InvalidArgumentError(f"path is blank")

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


class Language(Enum):
    PYTHON = "python"
    CSHARP = "csharp"
    VBNET = "vbnet"
    JAVA = "java"
    KOTLIN = "kotlin"

    @classmethod
    def from_str(cls, language_str: str) -> Language:
        languages: dict[str, Language] = {
            "python": cls.PYTHON,
            "csharp": cls.CSHARP,
            "vbnet": cls.VBNET,
            "java": cls.JAVA,
            "kotlin": cls.KOTLIN,
        }

        try:
            return languages[language_str.strip().lower()]
        except KeyError as ex:
            raise errors.InvalidArgumentError(
                f"unsupported language: '{language_str}': {ex}"
            ) from ex


@dataclass(frozen=True)
class LanguageTemplateInfo:
    display_name: str
    template_filename: str
    source_filename_pattern: re.Pattern[str]


# 対応言語が増えた場合はここに要素を追加してください。
# プログラム内からの更新はしないでください。
_LANGUAGE_INFO: dict[Language, LanguageTemplateInfo] = {
    Language.PYTHON: LanguageTemplateInfo(
        "Python", "review_py.template", re.compile(r"^.+\.py$")
    ),
    Language.CSHARP: LanguageTemplateInfo(
        "C#", "review_cs.template", re.compile(r"^.+\.cs$")
    ),
    Language.VBNET: LanguageTemplateInfo(
        "VB.NET", "review_vb.template", re.compile(r"^.+\.vb$")
    ),
    Language.JAVA: LanguageTemplateInfo(
        "Java", "review_java.template", re.compile(r"^.+\.java$")
    ),
    Language.KOTLIN: LanguageTemplateInfo(
        "Kotlin", "review_kt.template", re.compile(r"^.+\.kt$")
    ),
}


def get_language_default_filename_pattern(language: Language) -> re.Pattern[str]:
    try:
        return _LANGUAGE_INFO[language].source_filename_pattern
    except KeyError as ex:
        raise errors.InvalidStatusError(
            f"language filename pattern is not implemented: {language.value}: {ex}"
        ) from ex


def get_language_template_file_name(language: Language) -> str:
    return _LANGUAGE_INFO[language].template_filename


def get_template_display_name(language: Language) -> str:
    return _LANGUAGE_INFO[language].display_name
