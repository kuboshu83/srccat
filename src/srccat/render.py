from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections.abc import Sequence

import srccat.model as model

_MODULE_DIR = Path(__file__).resolve().parent

_TEMPLATES_DIR = _MODULE_DIR / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
)


def render_review_document(
    language: model.Language,
    srcfiles: Sequence[model.SrcFile],
    language_version: str | None = None,
) -> str:
    template = _env.get_template(language.template_filename)
    return template.render(
        language=language.display_name, language_version=language_version, srcs=srcfiles
    )

