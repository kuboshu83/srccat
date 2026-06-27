[!NOTE]
これはソースコードからAIで生成したREADMEで仮のものです。

# Source Review Document Builder

Source Review Document Builder は、指定したディレクトリ配下のソースコードを収集し、AIレビュー用のMarkdownドキュメントを生成するツールです。

Jinja2テンプレートを利用することで、レビュー指示や出力形式を自由にカスタマイズできます。

---

# 特徴

* ソースコードを再帰的に収集
* ファイルフィルタによる対象ファイルの絞り込み
* 除外ディレクトリの指定に対応
* Jinja2テンプレートによる柔軟な出力
* メモリ効率の良いGeneratorベースのファイル探索

---

# 対応言語

現在対応している言語

| 言語     |  対応 |
| ------ | :-: |
| Python |  ✅  |

---

# クイックスタート

```python
from pathlib import Path
import logging
import re

import collector
import model
from main import main

language = model.Language.from_str("Python")

filters = collector.FileFilters([
    collector.FileFilterByFileNamePattern(
        re.compile(r"^.+\.py$")
    )
])

file_collector = collector.FileCollector(
    srcdir=Path("."),
    filter=filters,
    recursive=True,
    exclude_dirs=[],
    logger=logging.getLogger("srccat"),
)

main(language, file_collector)
```

実行すると、レビュー用Markdownが標準出力へ出力されます。

---

# フィルタのカスタマイズ

独自のファイル選択条件を追加できます。

例：拡張子でフィルタする場合

```python
from pathlib import Path
import collector

class ExtensionFilter(collector.FileFilter):
    def __init__(self, ext: str):
        self._ext = ext

    def is_target(self, file: Path) -> bool:
        return file.suffix == self._ext
```

複数条件を組み合わせることもできます。

```python
filters = collector.FileFilters([
    ExtensionFilter(".py"),
    collector.FileFilterByFileNamePattern(
        re.compile(r".*test.*")
    ),
])
```

---

# 除外ディレクトリ

デフォルトで以下のディレクトリは探索対象外です。

* `.git`
* `.venv`
* `venv`
* `__pycache__`

さらに追加で除外したい場合は、

```python
exclude_dirs=[
    "build",
    "dist",
]
```

のように指定できます。

---

# テンプレート

出力内容は Jinja2 テンプレートで制御します。

テンプレートでは以下の変数が利用できます。

| 変数                 | 説明           |
| ------------------ | ------------ |
| `language`         | 言語名          |
| `language_version` | 言語バージョン      |
| `srcs`             | 収集したソースコード一覧 |

`srcs` の各要素は次のプロパティを持ちます。

| プロパティ      | 説明     |
| ---------- | ------ |
| `filepath` | ファイルパス |
| `code`     | ソースコード |

---

# 新しい言語を追加する

新しい言語を追加するには、

1. `Language` に追加する
2. 対応するテンプレートを作成する

例

```python
CPP = _LangInfo(
    "C++",
    "review_cpp.template",
)
```

テンプレート

```
templates/
    review_cpp.template
```

---

# 制限事項

* ソースコードは UTF-8 として読み込みます。
* シンボリックリンクは探索しません。
* 出力は標準出力へ行われます。

---

# 今後の予定

* CLI対応
* 対応言語の追加
* 出力先ファイル指定
* エンコーディング設定
* ファイルサイズ制限
* フィルタ機能の拡張
