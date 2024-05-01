# https://pypi.org/project/googletrans/
# NOTE: requires googletrans 4.0.0-rc1
from googletrans import Translator
translator = Translator()

supported_languages = [
    "English",
    "한굴",
    "日本語",
]

supported_languages_codes = [
    "en",
    "ko",
    "ja",
]

def IsValidLanguage(language):
    if language in supported_languages:
        return True
    print(f"Invalid language \"{language}\"")
    return False

def Translate(message, curr_language, language):
    if 0 == len(message): return ""
    if IsValidLanguage(curr_language) and IsValidLanguage(language):
        curr_language_code = supported_languages_codes[supported_languages.index(curr_language)]
        language_code = supported_languages_codes[supported_languages.index(language)]
        return translator.translate(message, dest=language_code, src=curr_language_code).text
    return message