from googletrans import Translator
from httpx import ReadTimeout


class TranslationService:
    def __init__(self):
        # googletrans client
        self._translator = Translator()

    def translate(self, text: str, target_language: str, source_language: str = "auto") -> dict:
        """
        Translates text to target_language.
        Source language defaults to 'auto' but can be specified.
        """
        try:
            result = self._translator.translate(
                text,
                dest=target_language,
                src=source_language
            )

            return {
                "translated_text": result.text,
                "detected_source_language": result.src
            }

        except ReadTimeout:
            # Expected with googletrans (network / rate-limit)
            raise RuntimeError(
                "Translation service timed out. Please try again."
            )

        except Exception as e:
            # Any other unexpected issue
            raise RuntimeError(
                "Translation failed due to network or service issue."
            ) from e