from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory


class RepoPinImgTranslator(GoogleTranslator):

    # 20 more commonly used languages supported by langdetect (~1-2 s per language translation)
    __COMMON_LANGS: list[str] = [
        "en",
        "es",
        "fr",
        "de",
        "pt",
        "ru",
        "zh-CN",
        "zh-TW",
        "ja",
        "ko",
        "ar",
        "hi",
        "it",
        "tr",
        "nl",
        "sv",
        "pl",
        "id",
        "th",
        "vi",
        "uk",
    ]
    # other languages supported by langdetect (deep_translate uses iw instead of he)
    __OTHER_LANGS: list[str] = [
        "af",
        "bg",
        "bn",
        "ca",
        "cs",
        "cy",
        "da",
        "el",
        "et",
        "fa",
        "fi",
        "gu",
        "he",
        "hr",
        "hu",
        "kn",
        "lt",
        "lv",
        "mk",
        "ml",
        "mr",
        "ne",
        "no",
        "pa",
        "ro",
        "sk",
        "sl",
        "so",
        "sq",
        "sw",
        "ta",
        "te",
        "tl",
        "ur",
    ]

    def __init__(self):
        super().__init__()
        DetectorFactory.seed = 42
        self.__dt_langs: list[str] = list(
            self.get_supported_languages(as_dict=True).values()
        )  # deep_translate langs

    def translate_all(self, input_txt: str) -> dict[str, str]:
        input_txt_lang: str = detect(text=input_txt)
        translations: dict[str, str] = dict()
        translations[input_txt_lang] = input_txt
        for target_lang in self.__COMMON_LANGS:
            if target_lang in self.__dt_langs:
                self.target = target_lang
                translations[target_lang] = self.translate(text=input_txt)
        return translations
