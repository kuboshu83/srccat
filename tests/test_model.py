import pytest
import srccat.model


class TestSrcFile:
    class TestConstructor:
        class TestAbnormal:
            @pytest.mark.parametrize("filepath", ["", " "])
            def test_invalid_filepath(self, filepath: str):
                with pytest.raises(ValueError):
                    srccat.model.SrcFile(filepath, "code")

            @pytest.mark.parametrize("code", ["", " "])
            def test_invalid_code(self, code: str):
                with pytest.raises(ValueError):
                    srccat.model.SrcFile("path", code)


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
