import pytest

import srccat.model as model
import srccat.errors as errors


class TestEncoding:
    class TestFromStr:
        class TestAbnormal:
            @pytest.mark.parametrize(
                "invalid_encoding_str",
                (
                    "",
                    " ",
                    "utf 8",
                    "utf=8",
                    "utf+8",
                    "ascii",
                ),
            )
            def test_invalid_encoding_string_throw(self, invalid_encoding_str: str):
                # act, assert
                with pytest.raises(errors.InvalidArgumentError):
                    model.Encoding.from_str(invalid_encoding_str)

        class TestNormal:
            @pytest.mark.parametrize(
                "encoding_str, encoding",
                [
                    [" shiftjis ", model.Encoding.SHIFTJIS],
                    [" shift-jis ", model.Encoding.SHIFTJIS],
                    [" shift_jis ", model.Encoding.SHIFTJIS],
                    [" utf8 ", model.Encoding.UTF8],
                    [" utf-8", model.Encoding.UTF8],
                    [" utf_8", model.Encoding.UTF8],
                    [" utf16 ", model.Encoding.UTF16],
                    [" utf-16", model.Encoding.UTF16],
                    [" utf_16", model.Encoding.UTF16],
                ],
            )
            def test_encoding_string_return_encoding(
                self, encoding_str: str, encoding: model.Encoding
            ):
                # act
                result = model.Encoding.from_str(encoding_str)

                # assert
                assert result == encoding


class TestLanguage:
    class TestFromStr:
        class TestAbnormal:
            @pytest.mark.parametrize(
                "invalid_language_str", ("ruby", "", " ", " python", "python ", "")
            )
            def test_invalid_language_string_throw(self, invalid_language_str: str):
                # act, assert
                with pytest.raises(errors.InvalidArgumentError):
                    model.Language.from_str(invalid_language_str)

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
            def test_valid_language_string_return_inctance(
                self, language_str: str, language: model.Language
            ):
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
