from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import override
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


class SourceCodeLoadResult(ABC):
    """
    SourceCodeの読み込みの成否を表すクラス
    """

    @abstractmethod
    def result(self) -> SuccessFail:
        pass

    @abstractmethod
    def error(self) -> Exception | None:
        pass


@dataclass(frozen=True)
class _SourceCodeLoadSuccess(SourceCodeLoadResult):
    @override
    def result(self) -> SuccessFail:
        return SuccessFail.Success

    @override
    def error(self) -> Exception | None:
        return None


@dataclass(frozen=True)
class _SourceCodeLoadFail(SourceCodeLoadResult):
    load_error: Exception

    @override
    def result(self) -> SuccessFail:
        return SuccessFail.Fail

    @override
    def error(self) -> Exception | None:
        return self.load_error


class LoadedSourceFile(ABC):
    @abstractmethod
    def filepath(self) -> str:
        pass

    @abstractmethod
    def code(self) -> str | None:
        pass

    @abstractmethod
    def result(self) -> SourceCodeLoadResult:
        pass


@dataclass(frozen=True)
class SuccessLoadedSourceFile(LoadedSourceFile):
    loaded_filepath: str
    loaded_code: str

    @override
    def filepath(self) -> str:
        return self.loaded_filepath

    @override
    def code(self) -> str | None:
        return self.loaded_code

    @override
    def result(self) -> SourceCodeLoadResult:
        return _SourceCodeLoadSuccess()


@dataclass(frozen=True)
class FailLoadedSourceFile(LoadedSourceFile):
    loaded_filepath: str
    error: Exception

    @override
    def filepath(self) -> str:
        return self.loaded_filepath

    @override
    def code(self) -> str | None:
        return None

    @override
    def result(self) -> SourceCodeLoadResult:
        return _SourceCodeLoadFail(self.error)


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
