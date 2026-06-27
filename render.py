from enum import Enum
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass

_MODULE_DIR = Path(__file__).resolve().parent


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


_TEMPLATES_DIR = _MODULE_DIR / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
)


def render_review_document(
    language: Language, language_version: str | None = None
) -> str:
    template = _env.get_template(language.template_filename)
    return template.render(language=language, language_version=language_version)


__all__ = ["Language", "render_review_document"]
