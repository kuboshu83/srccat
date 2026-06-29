from pathlib import Path
from pytest_mock import MockerFixture
import srccat.collector
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
        root / "test01.py",
        root / "test02.py",
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


class TestFileCollector:
    class TestCollectTargetFiles:
        class TestNormal:
            def test_return_files_no_recursive(
                self, tmp_path: Path, mocker: MockerFixture
            ):
                # arrange
                create_test_dir_structure(tmp_path)
                logger = mocker.Mock(spec=logging.Logger)
                rejector = srccat.collector.create_scan_directory_reject_filter(False, [])
                collector = srccat.collector.DFSDirectoryScanner(
                    scan_root_dir=tmp_path,
                    directory_rejector=rejector,
                    logger=logger,
                )

                # act
                files = list(collector.collect_files())

                # assert
                expected = [
                    tmp_path / "test01.py",
                    tmp_path / "test02.py",
                ]
                assert sorted(files) == sorted(expected)

            def test_return_files_recursive(
                self, tmp_path: Path, mocker: MockerFixture
            ):
                # arrange
                create_test_dir_structure(tmp_path)
                logger = mocker.Mock(spec=logging.Logger)
                policy = srccat.collector.create_scan_directory_reject_filter(True, [])
                collector = srccat.collector.DFSDirectoryScanner(
                    scan_root_dir=tmp_path,
                    directory_rejector=policy,
                    logger=logger,
                )

                # act
                files = list(collector.collect_files())

                # assert
                expected = [
                    tmp_path / "test01.py",
                    tmp_path / "test02.py",
                    tmp_path / "sub00" / "test04.py",
                    tmp_path / "sub00" / "sub10" / "test06.py",
                    tmp_path / "sub00" / "sub20" / "test07.py",
                ]
                assert sorted(files) == sorted(expected)
