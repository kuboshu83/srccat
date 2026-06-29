import pytest

import srccat.model  as model
import srccat.errors as errors


class TestLanguage:
    class TestDisplayName:
        class TestNormal:
            @pytest.mark.parametrize(
                "language, display_name", ((model.Language.PYTHON, "Python"),)
            )
            def test_return_name(
                self, language: model.Language, display_name: str
            ):
                # act
                name = language.display_name

                # assert
                assert name == display_name

    class TestTemplateFileName:
        class TestNormal:
            @pytest.mark.parametrize(
                "language, template_filename",
                ((model.Language.PYTHON, "review_py.template"),),
            )
            def test_return_name(
                self, language: model.Language, template_filename: str
            ):
                # act
                name = language.template_filename

                # assert
                assert name == template_filename

    class TestFromStr:
        class TestNormal:
            @pytest.mark.parametrize(
                "language_str, language",
                (
                    ("python", model.Language.PYTHON),
                    ("Python", model.Language.PYTHON),
                    ("PYTHON", model.Language.PYTHON),
                ),
            )
            def test_return_language(
                self, language_str: str, language: model.Language
            ):
                # act
                lang = model.Language.from_str(language_str)

                # assert
                assert lang == language

        class TestAbnormal:
            @pytest.mark.parametrize(
                "language_str",
                ("", " ", "ruby", "ぱいそん", " python", "python ", "py thon"),
            )
            def test_unsupported_language(self, language_str: str):
                with pytest.raises(ValueError):
                    model.Language.from_str(language_str)


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
