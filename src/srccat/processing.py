import base64
import io

import srccat.errors as errors

"""
文字列を加工するための機能を集めたモジュール
"""


# Chat AIにファイルを貼り付けた際にインデントが崩れたりする場合がある。
# その際、ファイルの内容をbase64でエンコードしたものをChatAIに渡す。
def convert_to_base64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


# 読み込んだソースコードの先頭に行番号を追加するために使用する。
def add_line_number_to_head(text: str, max_line_no: int) -> str:
    if max_line_no <= 0:
        raise errors.InvalidArgumentError(
            f"max line number must be >0 but {max_line_no}"
        )

    digits = len(str(max_line_no))

    processed_texts: list[str] = []
    for line_no, line in enumerate(io.StringIO(text), start=1):
        line = line.rstrip("\n")
        if line_no > max_line_no:
            raise errors.TooManyLinesError(
                f"line number exceed limit: line_no={line_no}, limit={max_line_no}"
            )
        line_no_str = f"[{line_no:0{digits}d}]"
        processed_texts.append(f"{line_no_str}: {line}")
    return "\n".join(processed_texts)
