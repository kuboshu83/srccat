import base64
import io
import re

import srccat.errors as errors

"""
文字列を加工するための機能を集めたモジュール
"""


# Chat AIにファイルを貼り付けた際にインデントが崩れたりする場合がある。
# その際、ファイルの内容をbase64でエンコードしたものをChatAIに渡す。
def convert_to_base64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def add_no_to_head(text: str, number: int, digits: int) -> str:
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


# 読み込んだソースコードの先頭に行番号を追加するために使用する。
def add_line_number_to_head(text: str, max_line_no: int) -> str:
    if max_line_no <= 0:
        raise errors.InvalidArgumentError(
            f"max line number must be >0 but {max_line_no}"
        )

    digits = len(str(max_line_no))

    processed_text: list[str] = []
    for line_no, line in enumerate(io.StringIO(text), start=1):
        line = line.rstrip("\n")
        if line_no > max_line_no:
            raise errors.TooManyLinesError(
                f"line number exceed limit: line_no={line_no}, limit={max_line_no}"
            )
        processed_line = add_no_to_head(line, line_no, digits)
        processed_line = remove_empty_line(processed_line)
        if processed_line != "":
            processed_text.append(processed_line)
    return "\n".join(processed_text)
