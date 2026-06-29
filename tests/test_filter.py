import srccat.filefilter
import re
import pytest
from pathlib import Path
from typing import override


class TestFileNameFilter:
    class TestIsTarget:
        class TestNormal:
            @pytest.mark.parametrize("filename", (Path("sample.py"), Path("smp.py")))
            def test_return_true(self, filename: Path):
                # arrange
                pattern = re.compile(r"^[a-zA-Z]+\.py$")
                filter = srccat.filefilter.FileNameFilter(pattern)

                # act
                is_target = filter.is_target(filename)

                # assert
                assert is_target == True

            @pytest.mark.parametrize(
                "filename",
                (
                    Path(""),
                    Path("   "),
                    Path(" sample.py"),
                    Path("sample .py"),
                    Path("sample"),
                    Path("sample1.py"),
                ),
            )
            def test_return_false(self, filename: Path):
                # arrange
                pattern = re.compile(r"^[a-zA-Z]+\.py$")
                filter = srccat.filefilter.FileNameFilter(pattern)

                # act
                is_target = filter.is_target(filename)

                # assert
                assert is_target == False


class FakeFilter(srccat.filefilter.FileFilter):
    def __init__(self, value: bool):
        self._value = value

    @override
    def is_target(self, file: Path) -> bool:
        return self._value
