from dataclasses import dataclass
from enum import Enum
import re


@dataclass(frozen=True)
class _EncodingInfo:
    id: str
    display_name: str
    codec: str


class Encoding(Enum):
    UTF8 = _EncodingInfo("utf8", "utf8", "utf-8")
    UTF16 = _EncodingInfo("utf16", "utf16", "utf-16")
    SHIFTJIS = _EncodingInfo("shiftjis", "shift-jis", "shift_jis")

    @property
    def display_name(self) -> str:
        return self.value.display_name

    @property
    def codec(self) -> str:
        return self.value.codec

    @classmethod
    def from_str(cls, encoding: str) -> Encoding:
        for encode in cls:
            if encode.value.id == encoding.lower():
                return encode
        raise ValueError(f"unsupported encoding: {encoding}")


class SuccessFail(Enum):
    Success = "success"
    Fail = "fail"


@dataclass
class SourceCodeLoadResult:
    result: SuccessFail
    error: Exception | None

    @classmethod
    def success(cls) -> SourceCodeLoadResult:
        return SourceCodeLoadResult(SuccessFail.Success, None)

    @classmethod
    def fail(cls, error: Exception) -> SourceCodeLoadResult:
        return SourceCodeLoadResult(SuccessFail.Fail, error)


@dataclass(frozen=True)
class LoadedSourceFile:
    filepath: str
    code: str
    load_result: SourceCodeLoadResult

    def __post_init__(self):
        # パスの判定は面倒なので、ここでは空の判定のみを行う。それ以外の無効なものは使用時の例外で検知する。
        if self.filepath.strip() == "":
            raise ValueError("file path is blank")
        if self.code.strip() == "":
            raise ValueError(f"code is blank: {self.filepath}")


@dataclass(frozen=True)
class _LangInfo:
    display_name: str
    template_filename: str
    filename_pattern: re.Pattern[str]


class Language(Enum):
    PYTHON = _LangInfo("Python", "review_py.template", re.compile(r"^.+\.py$"))

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
        raise ValueError(f"unsupported language: {language}")
