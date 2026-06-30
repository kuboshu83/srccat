import base64
import io
import re
from typing import Callable, Sequence

import srccat.errors as errors
import srccat.model as model

"""
文字列を加工するための機能を集めたモジュール
"""


# Chat AIにファイルを貼り付けた際にインデントが崩れたりする場合がある。
# その際、ファイルの内容をbase64でエンコードしたものをChatAIに渡す。
def convert_to_base64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def add_number_string_to_head(text: str, number: int, digits: int) -> str:
    """
    文字列の先頭に[0001]:のような文字列を追加します。
    桁数はdigitsで指定できますが、numberがdigitsの表現範囲を超えるとnumberに応じた桁数になります。
    """
    number_str = f"[{number:0{digits}d}]"
    return f"{number_str}: {text}"


# ソースコードのから行と行番号のみの行を削除します。
# ChatAIのコンテキスト長を節約するためです。
def remove_empty_line(text: str) -> str:
    """
    削除対象の行の場合はから文字を返します。
    削除対象でなければ入力された文字列をそのまま返します。

    Example:
    >>> remove_empty_line("\n")
    ''
    >>> remove_empty_line("[0001]:   \n")
    ''
    >>> remove_empty_line("not empty")
    'not empty'
    """
    # ソースコードの全行数分呼び出されるため、毎回patternを生成しないほうがいいかも。
    remove_pattern = re.compile(r"^(\[\d+]:)?\s*$")
    if remove_pattern.fullmatch(text):
        return ""
    return text


Processor = Callable[[str], str]


# 対応言語が増えたり、各言語に処理を追加したい場合はここに追加してください。
_PROCESSORS: dict[model.Language, Sequence[Processor]] = {
    model.Language.PYTHON: tuple(
        [
            remove_empty_line,
        ]
    ),
    model.Language.CSHARP: tuple(
        [
            remove_empty_line,
        ]
    ),
    model.Language.VBNET: tuple(
        [
            remove_empty_line,
        ]
    ),
    model.Language.JAVA: tuple(
        [
            remove_empty_line,
        ]
    ),
    model.Language.KOTLIN: tuple(
        [
            remove_empty_line,
        ]
    ),
}


def select_language_code_processors(
    language: model.Language,
) -> Sequence[Processor]:
    try:
        return _PROCESSORS[language]
    except KeyError as ex:
        raise errors.InvalidStatusError(
            f"language processors not registered: {language}: {ex}"
        ) from ex


def build_source_code_processor(
    max_line_number: int, language: model.Language
) -> Processor:
    processors = select_language_code_processors(language)

    if max_line_number <= 0:
        raise errors.InvalidArgumentError(
            f"max line number must be >0 but {max_line_number}"
        )

    digits = len(str(max_line_number))

    def _process_source_code(text: str) -> str:

        processed_text: list[str] = []
        for line_no, line in enumerate(io.StringIO(text), start=1):
            line = line.rstrip("\n")
            if line_no > max_line_number:
                raise errors.TooManyLinesError(
                    f"line number exceed limit: line_no={line_no}, limit={max_line_number}"
                )
            # 必ず最初の処理で行番号の追加を行う
            processed_line = add_number_string_to_head(line, line_no, digits)
            for processor in processors:
                processed_line = processor(processed_line)

            if processed_line != "":
                processed_text.append(processed_line)
        return "\n".join(processed_text)

    return _process_source_code
