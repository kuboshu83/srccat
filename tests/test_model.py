import pytest

import srccat.model as model
import srccat.errors as errors


class TestLanguage:
    class TestFromStr:
        class TestAbnormal:
            @pytest.mark.parametrize(
                "language_str", ("ruby", "", " ", " python", "python ", "")
            )
            def test_invalid_name_string(self, language_str: str):
                # act, assert
                with pytest.raises(errors.InvalidArgumentError):
                    model.Language.from_str(language_str)

        class TestNormal:
            @pytest.mark.parametrize(
                "language_str, language",
                (
                    ("python", model.Language.PYTHON),
                    ("csharp", model.Language.CSHARP),
                    ("vbnet", model.Language.VBNET),
                    ("java", model.Language.JAVA),
                    ("kotlin", model.Language.KOTLIN),
                ),
            )
            def test_name_string(self, language_str: str, language: model.Language):
                # act
                actual = model.Language.from_str(language_str)
                # assert
                expected = language
                assert actual == expected


class TestLoadResult:
    class TestConstructor:
        class TestAbnormal:
            def test_success_with_exception_throw(self):
                # act, assert
                with pytest.raises(errors.InvalidStatusError):
                    model.LoadResult(model.Result.Success, Exception())

            def test_fail_without_exception_throw(self):
                # act, assert
                with pytest.raises(errors.InvalidStatusError):
                    model.LoadResult(model.Result.Fail, None)


class TestLoadedSourceCode:
    class TestConstructor:
        class TestAbnormal:
            def test_empty_filepath_throw(self):
                # act, assert
                with pytest.raises(errors.InvalidArgumentError):
                    success = model.LoadResult.success()
                    model.LoadedSourceCode("", "code", success)

            def test_too_long_filepath_throw(self):
                # act, assert
                long_path = "a" * 300
                with pytest.raises(errors.InvalidArgumentError):
                    success = model.LoadResult.success()
                    model.LoadedSourceCode(long_path, "code", success)

        class TestNormal:
            def test_long_filepath_but_less_than_limit(self):
                # act
                long_path = "a" * 299
                success = model.LoadResult.success()
                model.LoadedSourceCode(long_path, "code", success)
                # インスタンスが生成できればパスなので、assertionによる検証は不要
