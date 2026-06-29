import srccat.filefilter as filefilter
import re
import pytest
from typing import override
from pathlib import Path


class TestFileNameFilter:
    class TestIsTarget:
        class TestNormal:
            @pytest.mark.parametrize("filename", (Path("sample.py"), Path("smp.py")))
            def test_return_true(self, filename: Path):
                # arrange
                pattern = re.compile(r"^[a-zA-Z]+\.py$")
                file_filter = filefilter.FileNameFilter(pattern)

                # act
                is_target = file_filter.is_target(filename)

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
                file_filter = filefilter.FileNameFilter(pattern)

                # act
                is_target = file_filter.is_target(filename)

                # assert
                assert is_target == False


class FakeFilter(filefilter.FileFilter):
    def __init__(self, value: bool):
        self._value = value

    @override
    def is_target(self, file: Path) -> bool:
        return self._value


class TestFileFilterOrCondition:
    class TestIsTarget:
        class TestNormal:
            def test_empty_filter_return_true(self):
                # arrange
                condition = filefilter.FileFilterOrCondition([])

                # act
                result = condition.is_target(Path("dummy"))

                # assert
                assert result

            def test_all_true_filter_return_true(self):
                # arrange
                condition = filefilter.FileFilterOrCondition(
                    [FakeFilter(True), FakeFilter(True), FakeFilter(True)]
                )

                # act
                result = condition.is_target(Path("dummy"))

                # assert
                assert result

            def test_contain_true_false_filter_return_true(self):
                # arrange
                condition = filefilter.FileFilterOrCondition(
                    [FakeFilter(True), FakeFilter(False), FakeFilter(True)]
                )

                # act
                result = condition.is_target(Path("dummy"))

                # assert
                assert result

            def test_all_false_filter_return_false(self):
                # arrange
                condition = filefilter.FileFilterOrCondition(
                    [FakeFilter(False), FakeFilter(False), FakeFilter(False)]
                )

                # act
                result = condition.is_target(Path("dummy"))

                # assert
                assert not result


class TestCreateFileNameFilter:
    class TestNormal:
        def test_empty_pattern_return_true(self):
            # arrange
            file_filter = filefilter.create_file_name_filter([])

            # act
            result = file_filter.is_target(Path("dummy.py"))

            # assert
            assert result

        def test_at_least_one_filter_matches_return_true(self):
            # arrange
            file_filter = filefilter.create_file_name_filter(
                [
                    re.compile("^.+.py$"),
                    re.compile("^.+.rb$"),
                ]
            )

            # act
            result = file_filter.is_target(Path("dummy.py"))

            # assert
            assert result

        def test_no_filter_matches_return_false(self):
            # arrange
            file_filter = filefilter.create_file_name_filter(
                [
                    re.compile("^.+.go$"),
                    re.compile("^.+.rb$"),
                ]
            )

            # act
            result = file_filter.is_target(Path("dummy.py"))

            # assert
            assert not result
