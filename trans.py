# DEFAULT_ENGINE = "google" # alternatively, "mymemory", "LibreTranslate"
DEFAULT_ENGINE = "LibreTranslate"

match DEFAULT_ENGINE:
    case "google":
        from googletrans import Translator
        translator = Translator(raise_exception=True)
        def trans(text: str, from_lang: str) -> str:
            """
            Translate the given text from the source language to English using the Google Translate API.

            Args:
                text (str): The text to be translated.
                from_lang (str): The source language (ISO 639-1 code).

            Returns:
                str: The translated text in English.
            """
            from_lang = "zh-CN" if from_lang == "zh" else from_lang
            translated_text = translator.translate(text, src=from_lang, dest="en").text
            return translated_text
    case "mymemory" | "LibreTranslate":
        from translate import Translator
        # create a dictionary of translators
        translators = {
            "zh": Translator(to_lang="en", from_lang="zh", provider=DEFAULT_ENGINE),
            "ar": Translator(to_lang="en", from_lang="ar", provider=DEFAULT_ENGINE),
            "fr": Translator(to_lang="en", from_lang="fr", provider=DEFAULT_ENGINE),
            "es": Translator(to_lang="en", from_lang="es", provider=DEFAULT_ENGINE),
            "ru": Translator(to_lang="en", from_lang="ru", provider=DEFAULT_ENGINE)
        }
        def trans(text: str, from_lang: str) -> str:
            """
            Translate the given text from the source language to English using the MyMemory or LibreTranslate API.

            Args:
                text (str): The text to be translated.
                from_lang (str): The source language (ISO 639-1 code).

            Returns:
                str: The translated text in English.

            Raises:
                ValueError: If the source language is unsupported.
            """
            if from_lang not in translators:
                raise ValueError(f"Unsupported language: {from_lang}")
            return translators[from_lang].translate(text)
    # case "local": # Translation using local language models (not recommended)
    #     from transformers import pipeline
    #     translators = {
    #         # "zh": pipeline("translation_zh_to_en", model="Helsinki-NLP/opus-mt-zh-en"),
    #         "ar": pipeline("translation_ar_to_en", model="Helsinki-NLP/opus-mt-ar-en"),
    #         "fr": pipeline("translation_fr_to_en", model="Helsinki-NLP/opus-mt-fr-en"),
    #         "es": pipeline("translation_es_to_en", model="Helsinki-NLP/opus-mt-es-en"),
    #         "ru": pipeline("translation_ru_to_en", model="Helsinki-NLP/opus-mt-ru-en")
    #     }

    #     def trans(text: str, from_lang: str) -> str:
    #         if from_lang not in translators:
    #             raise ValueError(f"Unsupported language: {from_lang}")
    #         return translators[from_lang](text)[0]['translation_text']
    case _:
        raise ValueError(f"Unsupported engine: {DEFAULT_ENGINE}")
