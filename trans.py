from translate import Translator

# create a dictionary of translators
translators = {
    "zh": Translator(to_lang="en", from_lang="zh"),
    "ar": Translator(to_lang="en", from_lang="ar"),
    "fr": Translator(to_lang="en", from_lang="fr"),
    "es": Translator(to_lang="en", from_lang="es"),
    "ru": Translator(to_lang="en", from_lang="ru")
}

# translators["zh"].translate("你好")

#define a function to translate text
def trans(text: str, from_lang: str) -> str:
    if from_lang not in translators:
        raise ValueError(f"Unsupported language: {from_lang}")
    return translators[from_lang].translate(text)

# from transformers import pipeline
# translators = {
#     # "zh": pipeline("translation_zh_to_en", model="Helsinki-NLP/opus-mt-zh-en"),
#     "ar": pipeline("translation_ar_to_en", model="Helsinki-NLP/opus-mt-ar-en"),
#     "fr": pipeline("translation_fr_to_en", model="Helsinki-NLP/opus-mt-fr-en"),
#     "es": pipeline("translation_es_to_en", model="Helsinki-NLP/opus-mt-es-en"),
#     "ru": pipeline("translation_ru_to_en", model="Helsinki-NLP/opus-mt-ru-en")
# }

# def trans(text: str, from_lang: str) -> str:
#     if from_lang not in translators:
#         raise ValueError(f"Unsupported language: {from_lang}")
#     return translators[from_lang](text)[0]['translation_text']

# from googletrans import Translator

# translator = Translator()  # Initialize translator
# translator.raise_Exception = True
# translated_text = translator.translate(text, src=detected_language, dest="en").text
