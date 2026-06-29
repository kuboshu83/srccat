import srccat.filefilter
import re
import pytest
from pathlib import Path
from typing import override


class TestFileFilterByFileNamePattern:
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


class TestAndFilters:
    class TestIsTarget:
        class TestNormal:
            def test_empty_filter_return_true(self):
                # arrange
                filters = srccat.filefilter.AndFileFilters(())

                # act
                is_target = filters.is_target(Path(""))

                # assert
                assert is_target == True

            def test_return_true(self):
                # arrange
                filters = srccat.filefilter.AndFileFilters(
                    (FakeFilter(True), FakeFilter(True))
                )

                # act
                is_target = filters.is_target(Path(""))

                # assert
                assert is_target == True

            def test_return_false(self):
                # arrange
                filters = srccat.filefilter.AndFileFilters(
                    (FakeFilter(True), FakeFilter(False))
                )

                # act
                is_target = filters.is_target(Path(""))

                # assert
                assert is_target == False
