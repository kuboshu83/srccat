from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections.abc import Sequence

import srccat.model

_MODULE_DIR = Path(__file__).resolve().parent

_TEMPLATES_DIR = _MODULE_DIR / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
)


def render_review_document(
    language: srccat.model.Language,
    loaded_source_files: Sequence[srccat.model.LoadedSourceCode],
    language_version: str | None = None,
) -> str:
    template = _env.get_template(srccat.model.get_language_template_file_name(language))
    return template.render(
        language=srccat.model.get_template_display_name(language),
        language_version=language_version,
        loaded_source_files=loaded_source_files,
    )
