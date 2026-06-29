import pytest
import srccat.model

import srccat.errors as errors


class TestLanguage:
    class TestDisplayName:
        class TestNormal:
            @pytest.mark.parametrize(
                "language, display_name", ((srccat.model.Language.PYTHON, "Python"),)
            )
            def test_return_name(
                self, language: srccat.model.Language, display_name: str
            ):
                # act
                name = language.display_name

                # assert
                assert name == display_name

    class TestTemplateFileName:
        class TestNormal:
            @pytest.mark.parametrize(
                "language, template_filename",
                ((srccat.model.Language.PYTHON, "review_py.template"),),
            )
            def test_return_name(
                self, language: srccat.model.Language, template_filename: str
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
                    ("python", srccat.model.Language.PYTHON),
                    ("Python", srccat.model.Language.PYTHON),
                    ("PYTHON", srccat.model.Language.PYTHON),
                ),
            )
            def test_return_language(
                self, language_str: str, language: srccat.model.Language
            ):
                # act
                lang = srccat.model.Language.from_str(language_str)

                # assert
                assert lang == language

        class TestAbnormal:
            @pytest.mark.parametrize(
                "language_str",
                ("", " ", "ruby", "ぱいそん", " python", "python ", "py thon"),
            )
            def test_unsupported_language(self, language_str: str):
                with pytest.raises(ValueError):
                    srccat.model.Language.from_str(language_str)


class TestLoadResult:
    class TestConstructor:
        class TestAbnormal:
            def test_success_with_exception_throw(self):
                # act, assert
                with pytest.raises(errors.InvalidStatusError):
                    srccat.model.LoadResult(srccat.model.Result.Success, Exception())

            def test_fail_without_exception_throw(self):
                # act, assert
                with pytest.raises(errors.InvalidStatusError):
                    srccat.model.LoadResult(srccat.model.Result.Fail, None)


class TestLoadedSourceCode:
    class TestConstructor:
        class TestAbnormal:
            def test_empty_filepath_throw(self):
                # act, assert
                with pytest.raises(errors.InvalidArgumentError):
                    success = srccat.model.LoadResult.success()
                    srccat.model.LoadedSourceCode("", "code", success)

            def test_too_long_filepath_throw(self):
                # act, assert
                long_path = "a" * 300
                with pytest.raises(errors.InvalidArgumentError):
                    success = srccat.model.LoadResult.success()
                    srccat.model.LoadedSourceCode(long_path, "code", success)

        class TestNormal:
            def test_long_filepath_but_less_than_limit(self):
                # act
                long_path = "a" * 299
                success = srccat.model.LoadResult.success()
                srccat.model.LoadedSourceCode(long_path, "code", success)
                # インスタンスが生成できればパスなので、assertionによる検証は不要
