from pathlib import Path
from typing import override
from pytest_mock import MockerFixture
import srccat.collector
import srccat.filefilter
import logging


def create_test_dir_structure(root: Path):
    """
    ./
    |- test01.py
    |- test02.py
    |- .venv/
    |   |- test03.py
    |- sub00/
    |   |- test04.py
    |   |- venv/
    |   |   |- test05.py
    |   |- sub10/
    |   |   | - test06.py
    |   |- sub20/
    |   |   | - test07.py
    |- __pycache__/
    |   |- test08.py
    |- .git/
        |- test09.py
    """
    files = (
        root / "test01",
        root / "test02",
        root / ".venv" / "test03.py",
        root / "sub00" / "test04.py",
        root / "sub00" / "venv" / "test05.py",
        root / "sub00" / "sub10" / "test06.py",
        root / "sub00" / "sub20" / "test07.py",
        root / "__pycache__" / "test08.py",
        root / ".git" / "test09.py",
    )
    for file in files:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("")


class FakeFilter(srccat.filefilter.FileFilter):
    def __init__(self, value: bool):
        self._value = value

    @override
    def is_target(self, file: Path) -> bool:
        return self._value


class TestFileCollector:
    class TestCollectTargetFiles:
        class TestNormal:
            def test_return_files_no_recursive(
                self, tmp_path: Path, mocker: MockerFixture
            ):
                # arrange
                create_test_dir_structure(tmp_path)
                logger = mocker.Mock(spec=logging.Logger)
                collector = srccat.collector.FileCollector(
                    srcdir=tmp_path,
                    filter=FakeFilter(True),
                    recursive=False,
                    exclude_dirs=(),
                    logger=logger,
                )

                # act
                files = list(collector.collect_target_files())

                # assert
                expected = [
                    tmp_path / "test01",
                    tmp_path / "test02",
                ]
                assert sorted(files) == sorted(expected)

            def test_return_files_recursive(
                self, tmp_path: Path, mocker: MockerFixture
            ):
                # arrange
                create_test_dir_structure(tmp_path)
                logger = mocker.Mock(spec=logging.Logger)
                collector = srccat.collector.FileCollector(
                    srcdir=tmp_path,
                    filter=FakeFilter(True),
                    recursive=True,
                    exclude_dirs=(),
                    logger=logger,
                )

                # act
                files = list(collector.collect_target_files())

                # assert
                expected = [
                    tmp_path / "test01",
                    tmp_path / "test02",
                    tmp_path / "sub00" / "test04.py",
                    tmp_path / "sub00" / "sub10" / "test06.py",
                    tmp_path / "sub00" / "sub20" / "test07.py",
                ]
                assert sorted(files) == sorted(expected)
            
            def test_filter_reject_all_pattern_return_nothing(self, tmp_path:Path, mocker:MockerFixture):
                # arrange
                create_test_dir_structure(tmp_path)
                logger = mocker.Mock(spec=logging.Logger)
                collector = srccat.collector.FileCollector(
                    srcdir=tmp_path,
                    filter=FakeFilter(False),
                    recursive=True,
                    exclude_dirs=(),
                    logger=logger,
                )

                # act
                files = list(collector.collect_target_files())

                # assert
                assert files == []
