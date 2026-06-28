from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class SrcFile:
    filepath: str
    code: str

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


class Language(Enum):
    PYTHON = _LangInfo("Python", "review_py.template")

    @property
    def display_name(self) -> str:
        return self.value.display_name

    @property
    def template_filename(self) -> str:
        return self.value.template_filename

    @classmethod
    def from_str(cls, language: str) -> Language:
        for lang in cls:
            if lang.name == language.upper():
                return lang
        raise ValueError(f"unsupported language: {language}")
